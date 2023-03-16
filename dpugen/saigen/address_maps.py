#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *


class Mappings(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.num_yields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):

            eni_mac = str(
                macaddress.MAC(
                    int(macaddress.MAC(p.MAC_L_START)) + eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            self.num_yields += 1
            yield {
                'name': f'eni_ether_address_map_#eni{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'address': eni_mac
                },
                'attributes': [
                    'SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID', f'$eni_#{eni}',
                ]
            }


if __name__ == '__main__':
    conf = Mappings()
    common_main(conf)
