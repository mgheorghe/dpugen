#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *


class Vnets(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            for vnet_index in range(p.VNET_PER_ENI):
                vnet = eni + vnet_index

                self.num_yields += 1
                yield {
                    'name': 'vnet_#%d' % vnet,
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_VNET',
                    'attributes': [
                        'SAI_VNET_ATTR_VNI',
                        '%d' % (eni + p.ENI_L2R_STEP),
                    ]
                }


if __name__ == '__main__':
    conf = Vnets()
    common_main(conf)
