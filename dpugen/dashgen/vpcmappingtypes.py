#!/usr/bin/python3

import os
import sys

from confbase import ConfBase
from dashgen.confutils import common_main


class VpcMappingTypes(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)

        vpcmappingtypes = [
            "vpc",
            "privatelink",
            "privatelinknsg"
        ]

        # return generator from list for consistency with other subgenerators
        for x in vpcmappingtypes:

            self.num_yields += 1
            yield x


if __name__ == "__main__":
    conf = VpcMappingTypes()
    common_main(conf)
