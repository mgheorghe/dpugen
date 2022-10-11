#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class Vnets(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Vnets ...', file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            self.numYields += 1
            vnet_data = {
                'name': 'vnet_#%d' % eni,
                'type': 'SAI_OBJECT_TYPE_VNET',
                'attributes': [
                    'SAI_VNET_ATTR_VNI',
                    eni,
                ],
                'op': 'create',
            }

            yield vnet_data


if __name__ == '__main__':
    conf = Vnets()
    common_main(conf)
