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

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        OUTBOUND_ROUTES_PER_ACL = p.TOTAL_OUTBOUND_ROUTES // (p.ENI_COUNT * 2 * p.ACL_NSG_COUNT * p.ACL_RULES_NSG)

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
            for table_index in range(p.ACL_NSG_COUNT * 2):  # Per outbound group (5)
                IP_R_START_nsg = IP_R_START_eni + ip_int.IP_STEP_NSG * table_index
                for acl_index in range(0, p.ACL_RULES_NSG, 2):  # Per even rule (1000 / 2)

                    IP_RANGE_START = IP_R_START_nsg + p.IP_PER_ACL_RULE * acl_index - 1

                    routes = self.create_routes(IP_RANGE_START, p.IP_PER_ACL_RULE * 2)
                    routes = self.make_more_routes(routes, OUTBOUND_ROUTES_PER_ACL * 2)
                    routes = self.make_more_routes(routes, OUTBOUND_ROUTES_PER_ACL * 2)

                    for route in routes:
                        ip = socket_inet_ntoa(struct_pack('>L', route['ip']))
                        if acl_index < p.ACL_MAPPED_PER_NSG:

                            # routes that have a mac mapping
                            self.num_yields += 1
                            yield {
                                'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, ip, route['mask']): {
                                    'action_type': 'vnet',
                                    'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP)
                                },
                                'OP': 'SET'
                            }
                        else:
                            # routes that do not have a mac mapping
                            self.num_yields += 1
                            yield {
                                'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, ip, route['mask']): {
                                    'action_type': 'vnet_direct',
                                    'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP),
                                    'overlay_ip': gateway_ip
                                },
                                'OP': 'SET'
                            }
                    added_route_count += len(routes)

            # add a default route if no route was added to current ENI'
            if added_route_count == 0:
                remote_ip_prefix = socket_inet_ntoa(struct_pack('>L', ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI))
                if p.MAPPED_ACL_PER_NSG > 0:
                    self.num_yields += 1
                    yield {
                        'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, remote_ip_prefix, 10): {
                            'action_type': 'vnet',
                            'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP)
                        },
                        'OP': 'SET'
                    }
                # TODO: we can have a case where we have mapped and routed and we need both routes if route count is 0
                elif p.ACL_MAPPED_PER_NSG == 0:
                    self.num_yields += 1
                    yield {
                        'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, remote_ip_prefix, 10): {
                            'action_type': 'vnet_direct',
                            'vnet': 'vnet-%d' % (eni + p.ENI_L2R_STEP),
                            'overlay_ip': gateway_ip
                        },
                        'OP': 'SET'
                    }
                else:
                    raise Exception('ACL_MAPPED_PER_NSG <%d> cannot be < 0' % p.ACL_MAPPED_PER_NSG)


if __name__ == '__main__':
    conf = OutRouteRules()
    common_main(conf)
