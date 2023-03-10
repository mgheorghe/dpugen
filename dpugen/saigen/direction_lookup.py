#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *

TEMPLATE_DIRECTION_LOOKUP = {
    'name': 'direction_lookup_entry_#%(ENI)d',
    'op': 'create',
    'type': 'SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY',
    'key': {
        'switch_id': '$SWITCH_ID',
        'vni': '%(ENI)d',
    },
    'attributes': [
        'SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION',
        'SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION'
    ]
}


class DirectionLookup(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):

            self.num_yields += 1
            yield TEMPLATE_DIRECTION_LOOKUP % {
                'ENI': eni
            }


if __name__ == '__main__':
    conf = DirectionLookup()
    common_main(conf)
