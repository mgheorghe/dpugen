#!/usr/bin/python3

import math
import os
import sys

from dpugen.confbase import (
    ConfBase,
    ipa
)
from dpugen.confutils import common_main


class RouteTables(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        nr_of_routes_prefixes = int(math.log(p.IP_ROUTE_DIVIDER_PER_ACL_RULE, 2))
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI (64)
            vtep_eni = str(ipa(p.PAL) + int(ipa(p.IP_STEP1)) * eni_index)
            added_route_count = 0
            for table_index in range(p.ACL_NSG_COUNT):  # Per outbound group (5)
                for acl_index in range(p.ACL_RULES_NSG // 2):  # Per even rule (1000 / 2)
                    remote_ip = cp.IP_R_START + (eni_index * cp.IP_STEP_ENI) + (table_index * cp.IP_STEP_NSG) + (acl_index * cp.IP_STEP_ACL)
                    no_of_route_groups = p.IP_PER_ACL_RULE // (p.IP_ROUTE_DIVIDER_PER_ACL_RULE // 2)
                    for ip_index in range(0, no_of_route_groups):
                        ip_prefix = (remote_ip - 1) + (ip_index * p.IP_ROUTE_DIVIDER_PER_ACL_RULE * cp.IP_STEP1)
                        for prefix_index in range(nr_of_routes_prefixes, 0, -1):
                            nr_of_ips = 1 << (prefix_index - 1)
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
                                        "action_type": "vnet_direct",
                                        "vnet": "vnet-%d" % (eni + p.ENI_L2R_STEP),
                                        "overlay_ip": vtep_eni
                                    },
                                    "OP": "SET"
                                }

                            added_route_count += 1
                            ip_prefix = ip_prefix + cp.IP_STEP1 * nr_of_ips

                    # TODO: transition between mapped and routed ips

            # TODO: write condition check here to add a default route if no route was added to current ENI'
            if added_route_count == 0:
                remote_ip_prefix = cp.IP_R_START + eni_index * cp.IP_STEP_ENI
                self.num_yields += 1
                yield {
                    "DASH_ROUTE_TABLE:eni-%d:%s/%d" % (eni, remote_ip_prefix, 10): {
                        "action_type": "vnet",
                        "vnet": "vnet-%d" % (eni + p.ENI_L2R_STEP)
                    },
                    "OP": "SET"
                }


if __name__ == "__main__":
    conf = RouteTables()
    common_main(conf)
