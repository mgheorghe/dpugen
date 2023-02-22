#!/usr/bin/python3

import sys
import os

from dashgen.confbase import *
from dashgen.confutils import *


class Appliance(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            self.numYields += 1
            yield {
                'DASH_APPLIANCE_TABLE:appliance-%d' % eni: {
                    "sip": "221.0.0.1",
                    "vm_vni": f'{eni}'
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Appliance()
    common_main(conf)
