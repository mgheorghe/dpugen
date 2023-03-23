#!/usr/bin/python3
"""SAI generator for Direction Lookup"""

import os
import sys

from confbase import ConfBase

from saigen.confutils import common_main


class DirectionLookup(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):

            self.num_yields += 1
            yield {
                'name': f'direction_lookup_entry_#eni{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'vni': f'{eni}',
                },
                'attributes': [
                    'SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION', 'SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION'
                ]
            }


if __name__ == '__main__':
    conf = DirectionLookup()
    common_main(conf)
