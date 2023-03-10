#!/usr/bin/python3

import sys
import os

from dashgen.confbase import *
from dashgen.confutils import *


class VpcMappingTypes(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.num_yields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

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
