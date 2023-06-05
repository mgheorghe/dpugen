#!/usr/bin/python3

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class RouteRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            r_vni_id = eni + p.ENI_L2R_STEP
            vtep_remote = cp.PAR + eni_index * cp.IP_STEP1
            self.num_yields += 1
            yield {
                "DASH_ROUTE_RULE_TABLE:eni-%d:%d:%s/32" % (eni, r_vni_id, vtep_remote): {
                    "action_type": "decap",
                    "priority": "0",
                    # "protocol": "0",
                    "pa_validation": "true",
                    "vnet":  "vnet-%d" % r_vni_id
                },
                "OP": "SET"
            }


if __name__ == "__main__":
    conf = RouteRules()
    common_main(conf)
