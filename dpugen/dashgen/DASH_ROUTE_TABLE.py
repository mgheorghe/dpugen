#!/usr/bin/python3

import math
import os
import sys
from copy import deepcopy

from dashgen.confbase import ConfBase
from dashgen.confutils import common_main


class RouteTables(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        cc = 0
        nr_of_routes_prefixes = int(math.log(p.IP_ROUTE_DIVIDER_PER_ACL_RULE, 2))
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):

            ip_prefixes = []
            ip_prefixes_append = ip_prefixes.append

            IP_L = cp.IP_L_START + eni_index * cp.IP_STEP_ENI
            added_route_count = 0
            for table_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                for acl_index in range(1, (p.ACL_RULES_NSG+1)):
                    ip_map_count = 0
                    remote_ip = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + (table_index - 1) * cp.IP_STEP_NSG + (acl_index - 1) * cp.IP_STEP_ACL
                    no_of_route_groups = p.IP_PER_ACL_RULE * 2 // p.IP_ROUTE_DIVIDER_PER_ACL_RULE
                    for ip_index in range(0, no_of_route_groups):
                        ip_prefix = remote_ip - 1 + ip_index * p.IP_ROUTE_DIVIDER_PER_ACL_RULE * cp.IP_STEP1
                        for prefix_index in range(nr_of_routes_prefixes, 0, -1):
                            # nr_of_ips = int(math.pow(2, prefix_index-1))
                            nr_of_ips = 1 << (prefix_index-1)
                            mask = 32 - prefix_index + 1
                            if mask == 32:
                                ip_prefix = ip_prefix + 1

                            if (eni % 4) == 1:
                                self.num_yields += 1
                                yield {
                                    "DASH_ROUTE_TABLE:eni-%d:%s/%d" % (eni, ip_prefix, mask): {
                                        "action_type": "vnet",
                                        "vnet": "vnet-%d" % (eni + p.ENI_L2R_STEP)
                                    },
                                    "OP": "SET"
                                }

                            else:
                                # routes that do not have a mac mapping
                                self.num_yields += 1
                                yield {
                                    "DASH_ROUTE_TABLE:eni-%d:%s/%d" % (eni, ip_prefix, mask): {
                                        "action_type": "vnet",
                                        "vnet": "vnet-%d" % (eni + p.ENI_L2R_STEP)
                                    },
                                    "OP": "SET"
                                }

                            added_route_count += 1
                            ip_prefix = ip_prefix + cp.IP_STEP1 * nr_of_ips
                            ip_map_count += int(math.pow(2, (32 - mask)))

                    # TODO1: transition between mapped and routed ips

            # TODO: write condition check here to add a default route if no route was added so curent ENI'
            if added_route_count == 0:
                remote_ip_prefix = cp.IP_R_START + eni_index * cp.IP_STEP_ENI
                self.numYields += 1
                yield {
                    "DASH_ROUTE_TABLE:eni-%d:%s/%d" % (eni, remote_ip_prefix, 10): {
                        "action_type": "vnet",
                        "vnet": "vnet-%d" % (eni + p.ENI_L2R_STEP)
                    },
                    "OP": "SET"
                }
            # route_layers = deepcopy(
            #     {
            #         "Name": "LAYER_%d_ROUTE" % eni, "Type": 1,
            #         "Groups": [
            #             {
            #                 "Name": "GROUP_%d_OUT_ROUTE" % eni,
            #                 "Type": 0, "Direction": 0,
            #                 "Rules": {
            #                     "subnet_routes": routes
            #                 }
            #             },
            #             {
            #                 "Name": "GROUP_%d_IN_ROUTE" % eni,
            #                 "Type": 0,
            #                 "Direction": 1,
            #                 "Rules": [
            #                     {
            #                         "Name": "RULE_900%d_IN_ROUTE" % eni,
            #                         "Priority": 1,
            #                         "Action": 2,
            #                         "Conditions": [
            #                             {
            #                                 "VNIKeyList": [eni, (eni + ENI_L2R_STEP)]
            #                             }
            #                         ]
            #                     }
            #                 ]
            #             }
            #         ]
            #     }
            # )


if __name__ == "__main__":
    conf = RouteTables()
    common_main(conf)
