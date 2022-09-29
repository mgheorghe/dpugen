#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class DirectionLookup(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating DirectionLookup ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        vm_underlay_dip = ipaddress.ip_address(p.PAL)

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            vm_underlay_dip = vm_underlay_dip + int(ipaddress.ip_address(p.IP_STEP1))

            self.numYields += 1
            direction_lookup_data = {
                'name': 'direction_lookup_entry#%d' % eni,
                'type': 'SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'vni': eni,
                },
                'attributes': [
                    'SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION', 
                    'SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION'
                ],
                'op': 'create',
            }

            yield direction_lookup_data


if __name__ == '__main__':
    conf = DirectionLookup()
    common_main(conf)
