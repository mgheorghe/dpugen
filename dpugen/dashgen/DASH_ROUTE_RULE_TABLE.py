#!/usr/bin/python3

import sys
from copy import deepcopy
import os

from dashgen.confbase import *
from dashgen.confutils import *


class RouteRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        # optimizations:
        IP_STEP4 = cp.IP_STEP4
        IP_R_START = cp.IP_R_START
        IP_L_START = cp.IP_L_START
        ENI_COUNT = p.ENI_COUNT
        ENI_L2R_STEP = p.ENI_L2R_STEP

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            IP_L = IP_L_START + eni_index * IP_STEP4
            r_vpc = eni + ENI_L2R_STEP
            IP_R = IP_R_START + eni_index * IP_STEP4
            self.numYields += 1
            yield {
                "DASH_ROUTE_RULE_TABLE:eni-%d:%d:10.0.2.0/24" (eni, eni): {
                    "action_type": "decap",
                    "priority": "1",
                    "protocol": "0",
                    "pa_validation": "true",
                    "vnet": "Vnet2"
                },
                "OP": "SET"
            }

            self.numYields += 1
            yield {
                "DASH_ROUTE_RULE_TABLE:eni-%d:%d:10.0.2.0/24" (eni, r_vpc): {
                    "action_type": "decap",
                    "priority": "1",
                    "protocol": "0",
                    "pa_validation": "false"
                },
                "OP": "SET"
            }


if __name__ == "__main__":
    conf = RouteRules()
    common_main(conf)
