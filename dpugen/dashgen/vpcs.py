#!/usr/bin/python3

import os
import sys
from copy import deepcopy

from dashgen.confbase import ConfBase
from dashgen.confutils import common_main


class Vpcs(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.num_yields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        IP_L_START = cp.IP_L_START
        IP_R_START = cp.IP_R_START
        IP_STEP_ENI = cp.IP_STEP_ENI
        ENI_L2R_STEP = p.ENI_L2R_STEP
        ENI_COUNT = p.ENI_COUNT

        for eni_index in range(1, ENI_COUNT+1):
            IP_L = IP_L_START + (eni_index - 1) * IP_STEP_ENI
            r_vpc = eni_index + ENI_L2R_STEP
            IP_R = IP_R_START + (eni_index - 1) * IP_STEP_ENI
            self.num_yields += 1
            yield {
                "VPC:%d" % eni_index: {
                    "vpc-id": "vpc-%d" % eni_index,
                    "vni-key": eni_index,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/32" % IP_L
                    ]
                },
            }

            self.num_yields += 1
            yield {
                "VPC:%d" % r_vpc: {
                    "vpc-id": "vpc-%d" % r_vpc,
                    "vni-key": r_vpc,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/9" % IP_R
                    ]
                },
            }


if __name__ == "__main__":
    conf = Vpcs()
    common_main(conf)
