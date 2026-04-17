#!/usr/bin/python3
"""DASH generator for Outbound Routing"""

import math
import os
import sys
from operator import itemgetter

from dpugen.confbase import (
    ConfBase,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main
import ipaddress


class OutRouteRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def get_max_mask(self, ip, count):
        mask_count = int(math.log2(count))
        IP_RANGE_START_BIN = str(bin(ip))
        mask_ip = len(IP_RANGE_START_BIN) - IP_RANGE_START_BIN.rfind('1') - 1
        if mask_count > mask_ip:
            return mask_ip
        else:
            return mask_count

    def create_routes(self, ip, count):
        routes = []
        mask = self.get_max_mask(ip, count)
        routes.append({'ip': ip, 'mask': 32 - mask})
        cate = int(math.pow(2, mask))
        next_count = count - cate
        next_ip = ip + cate

        if next_count > 0:
            routes.extend(self.create_routes(next_ip, next_count))

        return routes

    def split_route(self, route):
        routes = []

        if route['mask'] == 31:
            routes.append({'ip': route['ip'] + 1, 'mask': 32})
        elif route['mask'] < 31:
            routes.append({'ip': route['ip'], 'mask': route['mask'] + 1})
            routes.extend(self.split_route({'ip': route['ip'] + int(math.pow(2, 32 - route['mask'] - 1)), 'mask': route['mask'] + 1}))
        else:
            routes.append(route)

        return routes

    def make_more_routes(self, routes, count):
        more_routes = []
        nr_of_routes = len(routes)
        more = count - nr_of_routes

        if count <= nr_of_routes:
            for route in routes:
                if route['mask'] == 31:
                    more_routes.append({'ip': route['ip'] + 1, 'mask': 32})
                else:
                    more_routes.append(route)
            return more_routes

        routes = sorted(routes, key=itemgetter('mask'), reverse=False)

        for route in routes:
            if more >= (32 - route['mask'] - 1):
                tmp_r = self.split_route(route)
                more_routes.extend(tmp_r)
                more -= len(tmp_r)
            else:
                if route['mask'] == 31:
                    more_routes.append({'ip': route['ip'] + 1, 'mask': 32})
                else:
                    more_routes.append(route)

        more_routes = sorted(more_routes, key=itemgetter('ip'), reverse=False)
        return more_routes

    def decompose_block(self, base_ip, block_bits):
        # Non-summarizable decomposition of a 2^block_bits-IP block. Gap at base_ip+0.
        # When base_ip is aligned to its block size and allow IPs sit at odd offsets,
        # the gap falls on a deny/unused IP, so every allow IP in the block is covered.
        # Emits: /32 at base+1, /31 at base+2, /30 at base+4, ..., /(33-block_bits) at base+2^(block_bits-1).
        return [{'ip': base_ip + (1 << i), 'mask': 32 - i} for i in range(block_bits)]

    def pick_block_mix(self, ips, target):
        # Return [(block_bits, count), ...] tiling `ips` addresses into blocks whose
        # non-summarizable decompositions sum to exactly `target` routes.
        # Tries single-block first, then a two-block mix (preferring adjacent block sizes).
        # Falls back to an approximate single-block tile if no exact solution exists.
        for bb in range(1, 17):
            bs = 1 << bb
            if bs > ips:
                break
            if ips % bs == 0 and (ips // bs) * bb == target:
                return [(bb, ips // bs)]
        for gap in range(1, 17):
            for k1 in range(1, 17 - gap):
                k2 = k1 + gap
                bs1, bs2 = 1 << k1, 1 << k2
                if bs2 > ips:
                    break
                det = bs1 * k2 - bs2 * k1
                if det == 0:
                    continue
                x_num = ips * k2 - target * bs2
                y_num = target * bs1 - ips * k1
                if x_num % det or y_num % det:
                    continue
                X, Y = x_num // det, y_num // det
                if X >= 0 and Y >= 0:
                    return [(k1, X), (k2, Y)]
        best_bb, best_r = 1, 0
        for bb in range(1, 17):
            bs = 1 << bb
            if bs > ips:
                break
            r = (ips // bs) * bb
            if r <= target and r > best_r:
                best_bb, best_r = bb, r
        return [(best_bb, ips // (1 << best_bb))]

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        OUTBOUND_ROUTES_PER_ENI = p.TOTAL_OUTBOUND_ROUTES // p.ENI_COUNT

        # Routes are laid out per NSG: each NSG has its own IP window (IP_STEP_NSG apart)
        # so per-NSG tiling is required to cover allow IPs in all NSGs.
        num_nsg_groups = p.ACL_NSG_COUNT * 2
        ips_per_nsg = p.ACL_RULES_NSG * p.IP_PER_ACL_RULE
        target_per_nsg = OUTBOUND_ROUTES_PER_ENI // num_nsg_groups if num_nsg_groups else 0
        block_mix = self.pick_block_mix(ips_per_nsg, target_per_nsg) if (ips_per_nsg and target_per_nsg) else []
        mapped_ips_per_nsg = p.ACL_MAPPED_PER_NSG * p.IP_PER_ACL_RULE

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            print(f'    route:eni:{eni}', file=sys.stderr)
            IP_R_START_eni = ip_int.IP_R_START + ip_int.IP_STEP_ENI * eni_index
            if p.ACL_MAPPED_PER_NSG > 0:
                gateway_ip =  socket_inet_ntoa(struct_pack('>L', ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI))
            elif p.ACL_MAPPED_PER_NSG == 0:
                gateway_ip =  socket_inet_ntoa(struct_pack('>L', ip_int.GATEWAY + ip_int.IP_STEP1 * eni_index))
            else:
                raise Exception('ACL_MAPPED_PER_NSG <%d> cannot be < 0' % p.ACL_MAPPED_PER_NSG)

            added_route_count = 0
            for table_index in range(num_nsg_groups):
                # IP_R_START ends in .1 by convention; -1 shifts to a power-of-2 boundary.
                nsg_base = IP_R_START_eni + ip_int.IP_STEP_NSG * table_index - 1
                offset = 0
                for bb, count in block_mix:
                    bs = 1 << bb
                    for _ in range(count):
                        is_mapped = offset < mapped_ips_per_nsg
                        base_ip = nsg_base + offset
                        for r in self.decompose_block(base_ip, bb):
                            ip = socket_inet_ntoa(struct_pack('>L', r['ip']))
                            self.num_yields += 1
                            if is_mapped:
                                # routes that have a mac mapping
                                yield {
                                    'DASH_ROUTE_TABLE:route-group-%d:%s/%d' % (eni, ip, r['mask']): {
                                        'routing_type': 'vnet',
                                        'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP)
                                    },
                                    'OP': 'SET'
                                }
                            else:
                                # routes that do not have a mac mapping
                                yield {
                                    'DASH_ROUTE_TABLE:route-group-%d:%s/%d' % (eni, ip, r['mask']): {
                                        'routing_type': 'vnet_direct',
                                        'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP),
                                        'overlay_ip': gateway_ip
                                    },
                                    'OP': 'SET'
                                }
                        added_route_count += bb
                        offset += bs

            # add a default route if no route was added to current ENI'
            if added_route_count == 0:
                remote_ip_prefix = socket_inet_ntoa(struct_pack('>L', ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI))
                network = ipaddress.IPv4Network('%s/10' % remote_ip_prefix, strict=False)
                if p.ACL_MAPPED_PER_NSG > 0:
                    self.num_yields += 1
                    yield {
                        'DASH_ROUTE_TABLE:route-group-%d:%s' % (eni, network): {
                            'routing_type': 'vnet',
                            'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP)
                        },
                        'OP': 'SET'
                    }
                # TODO: we can have a case where we have mapped and routed and we need both routes if route count is 0
                elif p.ACL_MAPPED_PER_NSG == 0:
                    self.num_yields += 1
                    yield {
                        'DASH_ROUTE_TABLE:route-group-%d:%s' % (eni, network): {
                            'routing_type': 'vnet_direct',
                            'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP),
                            'overlay_ip': gateway_ip
                        },
                        'OP': 'SET'
                    }
                else:
                    raise Exception('ACL_MAPPED_PER_NSG <%d> cannot be < 0' % p.ACL_MAPPED_PER_NSG)

            # add local ENI IP route
            local_ip = socket_inet_ntoa(struct_pack('>L', ip_int.IP_L_START + eni_index * ip_int.IP_STEP_ENI))
            self.num_yields += 1
            yield {
                'DASH_ROUTE_TABLE:route-group-%d:%s/32' % (eni, local_ip): {
                    'routing_type': 'vnet',
                    'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP)
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = OutRouteRules()
    common_main(conf)
