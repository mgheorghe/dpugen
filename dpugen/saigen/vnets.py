#!/usr/bin/python3
"""SAI generator for VNET"""

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class Vnets(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):

            self.num_yields += 1
            yield {
                'name': f'vnet_#eni{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_VNET',
                'attributes': [
                    'SAI_VNET_ATTR_VNI', '%d' % (eni + p.ENI_L2R_STEP),
                ]
            }


if __name__ == '__main__':
    conf = Vnets()
    common_main(conf)
