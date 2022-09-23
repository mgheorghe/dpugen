#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class Vips(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Vips ...', file=sys.stderr)
        p = self.params

        self.numYields += 1
        vip_data = {
            'name': 'vip#1',
            'type': 'OBJECT_TYPE_VIP_ENTRY',
            'key': {
                'SWITCH': '$switch',
                'VIP': p.LOOPBACK
            },
            'attributes': [
                'SAI_VIP_ENTRY_ATTR_ACTION', 
                'SAI_VIP_ENTRY_ACTION_ACCEPT',
            ],
            'op': 'create',
        }

        yield vip_data


if __name__ == '__main__':
    conf = Vips()
    common_main(conf)
