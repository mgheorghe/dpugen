#!/usr/bin/python3

import math
import os
import sys
from operator import itemgetter

from dpugen.confbase import (
    ConfBase,
    ipa
)
from dpugen.confutils import common_main


class RouteTables(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0


    def get_max_mask_from_count(self, count):
        return int(math.log2(count))

    def get_max_mask_from_ip(self, ip):
        IP_RANGE_START_BIN = str(bin(ip))
        return len(IP_RANGE_START_BIN) - IP_RANGE_START_BIN.rfind('1') - 1

    def get_max_mask(self, ip, count):
        mask_count = self.get_max_mask_from_count(count)
        mask_ip = self.get_max_mask_from_ip(ip)
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
            routes.append(            {'ip': route['ip']    , 'mask': route['mask']+1})
            routes.extend(self.split_route({'ip': route['ip'] + int(math.pow(2, 32 - route['mask'] - 1)), 'mask': route['mask'] + 1}))
        else:
            routes.append(route)
    
        return routes

    def make_more_routes(self, routes, count):
        more_routes = []
        nr_of_routes = len(routes)
        more = count - nr_of_routes
        route_dict = []

        if count <= nr_of_routes:
            for route in routes:
                if route['mask'] == 31:
                    more_routes.append({'ip': route['ip'] + 1, 'mask': 32})
                else:
                    more_routes.append(route)
            return more_routes

        routes = sorted(routes, key=itemgetter('mask'), reverse=False)

        for route in routes:
            #text_route = '%s/%d' % (str(ipa(route['ip'])), route['mask'])
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
        cp = self.cooked_params

        TOTAL_OUTBOUND_ROUTES = p.TOTAL_OUTBOUND_ROUTES
        ENI_COUNT = p.ENI_COUNT
        ACL_NSG_COUNT = p.ACL_NSG_COUNT
        ACL_RULES_NSG = p.ACL_RULES_NSG
        IP_R_START = p.IP_R_START
        IP_STEP_ENI = p.IP_STEP_ENI
        IP_STEP_NSG = p.IP_STEP_NSG
        IP_STEP1 = p.IP_STEP1
        ENI_START = p.ENI_START
        ENI_STEP = p.ENI_STEP
        ENI_L2R_STEP = p.ENI_L2R_STEP
        PAL = p.PAL
        IP_PER_ACL_RULE = p.IP_PER_ACL_RULE

        OUTBOUND_ROUTES_PER_ACL = TOTAL_OUTBOUND_ROUTES // (ENI_COUNT * 2 * ACL_NSG_COUNT * ACL_RULES_NSG)

        IP_R_START_int = int(ipa(IP_R_START))
        IP_STEP_ENI_int = int(ipa(IP_STEP_ENI))
        IP_STEP1_int = int(ipa(IP_STEP1))
        IP_STEP_NSG_int = int(ipa(IP_STEP_NSG))

        for eni_index, eni in enumerate(range(ENI_START, ENI_START + ENI_COUNT * ENI_STEP, ENI_STEP)):  # Per ENI (64)
            print(eni)
            IP_R_START_eni_int = IP_R_START_int + IP_STEP_ENI_int * eni_index
            vtep_eni = str(ipa(PAL) + IP_STEP1_int * eni_index)
            added_route_count = 0
            for table_index in range(ACL_NSG_COUNT * 2):  # Per outbound group (5)
                IP_R_START_nsg_int = IP_R_START_eni_int + IP_STEP_NSG_int * table_index
                for acl_index in range(0, ACL_RULES_NSG, 2):  # Per even rule (1000 / 2)

                    IP_RANGE_START = IP_R_START_nsg_int + IP_PER_ACL_RULE * acl_index - 1
                    #IP_RANGE_END = IP_RANGE_START + 2 * IP_PER_ACL_RULE - 1

                    routes = self.create_routes(IP_RANGE_START, IP_PER_ACL_RULE * 2)
                    routes = self.make_more_routes(routes, OUTBOUND_ROUTES_PER_ACL * 2)
                    routes = self.make_more_routes(routes, OUTBOUND_ROUTES_PER_ACL * 2)

                    for route in routes:
                        if (eni % 4) == 1:
                            self.num_yields += 1
                            yield {
                                'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, str(ipa(route['ip'])), route['mask']): {
                                    'action_type': 'vnet',
                                    'vnet': 'vnet-%d' % (eni + ENI_L2R_STEP)
                                },
                                'OP': 'SET'
                            }
                        else:
                            # routes that do not have a mac mapping
                            self.num_yields += 1
                            yield {
                                'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, str(ipa(route['ip'])), route['mask']): {
                                    'action_type': 'vnet_direct',
                                    'vnet': 'vnet-%d' % (eni + ENI_L2R_STEP),
                                    'overlay_ip': vtep_eni
                                },
                                'OP': 'SET'
                            }
                    added_route_count += len(routes)
                            
            # TODO: write condition check here to add a default route if no route was added to current ENI'
            if added_route_count == 0:
                remote_ip_prefix = cp.IP_R_START + eni_index * cp.IP_STEP_ENI
                self.num_yields += 1
                yield {
                    'DASH_ROUTE_TABLE:eni-%d:%s/%d' % (eni, remote_ip_prefix, 10): {
                        'action_type': 'vnet',
                        'vnet': 'vnet-%d' % (eni + ENI_L2R_STEP)
                    },
                    'OP': 'SET'
                }


if __name__ == '__main__':
    conf = RouteTables()
    common_main(conf)
