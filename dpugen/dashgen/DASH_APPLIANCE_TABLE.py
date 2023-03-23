#!/usr/bin/python3

import os
import sys

from confbase import ConfBase

from dashgen.confutils import common_main


class Appliance(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            self.num_yields += 1
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
