#!/usr/bin/python3

import math
import sys
from copy import deepcopy
import os

from dashgen.confbase import *
from dashgen.confutils import *


class RouteTables(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        # optimizations:
        IP_ROUTE_DIVIDER_PER_ACL_RULE = p.IP_ROUTE_DIVIDER_PER_ACL_RULE
        IP_PER_ACL_RULE = p.IP_PER_ACL_RULE
        IP_STEP1 = cp.IP_STEP1
        IP_STEP2 = cp.IP_STEP2
        IP_STEP3 = cp.IP_STEP3
        IP_STEP4 = cp.IP_STEP4
        IP_R_START = cp.IP_R_START
        IP_L_START = cp.IP_L_START
        ACL_TABLE_COUNT = p.ACL_TABLE_COUNT
        ACL_RULES_NSG = p.ACL_RULES_NSG
        ENI_L2R_STEP = p.ENI_L2R_STEP

        nr_of_routes_prefixes = int(math.log(p.IP_ROUTE_DIVIDER_PER_ACL_RULE, 2))
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            routes = []
            ip_prefixes = []
            ip_prefixes_append = ip_prefixes.append

            IP_L = IP_L_START + eni_index * IP_STEP4
            r_vpc = eni_index + ENI_L2R_STEP
            # IP_R = IP_R_START + eni_index * IP_STEP4
            routes.append(
                {
                    "ip-prefixes": ["%s/32" % IP_L],
                    "action": {
                        "routing-type": "vpc",
                        "vpc-id": "vpc-%d" % eni_index
                    }
                }
            )

            for table_index in range(1, (ACL_TABLE_COUNT*2+1)):
                #table_id = eni_index * 1000 + table_index

                for acl_index in range(1, (ACL_RULES_NSG+1)):
                    remote_ip = IP_R_START + eni_index * IP_STEP4 + (table_index - 1) * 4 * IP_STEP3 + (acl_index - 1) * IP_STEP2
                    no_of_route_groups = IP_PER_ACL_RULE // IP_ROUTE_DIVIDER_PER_ACL_RULE
                    for ip_index in range(0, no_of_route_groups):
                        ip_prefix = remote_ip - 1 + ip_index * IP_ROUTE_DIVIDER_PER_ACL_RULE * IP_STEP1
                        for prefix_index in range(nr_of_routes_prefixes, 0, -1):
                            # nr_of_ips = int(math.pow(2, prefix_index-1))
                            nr_of_ips = 1 << (prefix_index-1)
                            mask = 32 - prefix_index + 1
                            if mask == 32:
                                ip_prefix = ip_prefix + 1

                            self.numYields += 1
                            yield {
                                "DASH_ROUTE_TABLE:eni-%d:%s/%d" % (eni, ip_prefix, mask): {
                                    "action_type": "vnet",
                                    "vnet": "Vnet2"
                                },
                                "OP": "SET"
                            }

                            ip_prefix = ip_prefix + IP_STEP1 * nr_of_ips


if __name__ == "__main__":
    conf = RouteTables()
    common_main(conf)
