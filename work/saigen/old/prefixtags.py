#!/usr/bin/python3

import sys

from saigen.confbase import ConfBase
from saigen.confutils import common_main


class PrefixTags(ConfBase):

    def __init__(self, params={}):
        super().__init__('prefix-tags', params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        for eni_index in range(1, p.ENI_COUNT+1):
            IP_L = cp.IP_L_START + (eni_index - 1) * cp.IP_STEP_ENI
            r_vpc = eni_index + p.ENI_L2R_STEP
            IP_R = cp.IP_R_START + (eni_index - 1) * cp.IP_STEP_ENI
            self.num_yields += 1
            yield \
                {
                    "PREFIX-TAG:VPC:%d" % eni_index: {
                        "prefix-tag-id": "%d" % eni_index,
                        "prefix-tag-number": eni_index,
                        "ip-prefixes-ipv4": [
                            "%s/32" % IP_L
                        ]
                    },
                }

            self.num_yields += 1
            yield \
                {
                    "PREFIX-TAG:VPC:%d" % r_vpc: {
                        "prefix-tag-id": "%d" % r_vpc,
                        "prefix-tag-number": r_vpc,
                        "ip-prefixes-ipv4": [
                            "%s/9" % IP_R
                        ]
                    },
                }


if __name__ == "__main__":
    conf = PrefixTags()
    common_main(conf)
