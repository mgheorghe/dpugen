#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *

TEMPLATE_VIP = {
    'name': 'vip_#1',
    'op': 'create',
    'type': 'SAI_OBJECT_TYPE_VIP_ENTRY',
    'key': {
        'switch_id': '$SWITCH_ID',
        'vip': '%(LOOPBACK)d'
    },
    'attributes': [
        'SAI_VIP_ENTRY_ATTR_ACTION',
        'SAI_VIP_ENTRY_ACTION_ACCEPT',
    ]
}


class Vips(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        self.num_yields += 1
        yield TEMPLATE_VIP % {
            'LOOPBACK': p.LOOPBACK
        }


if __name__ == '__main__':
    conf = Vips()
    common_main(conf)
