#!/usr/bin/python3
"""SAI generator for VIP"""

import os
import sys

from confbase import ConfBase
from saigen.confutils import common_main


class Vips(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        self.num_yields += 1
        yield {
            'name': 'vip_#1',
            'op': 'create',
            'type': 'SAI_OBJECT_TYPE_VIP_ENTRY',
            'key': {
                'switch_id': '$SWITCH_ID',
                'vip': p.LOOPBACK
            },
            'attributes': [
                'SAI_VIP_ENTRY_ATTR_ACTION', 'SAI_VIP_ENTRY_ACTION_ACCEPT',
            ]
        }


if __name__ == '__main__':
    conf = Vips()
    common_main(conf)
