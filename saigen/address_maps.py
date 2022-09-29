#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class AddressMaps(ConfBase):
    '''Configures the MAC value of the ENI'''

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating address maps ...', file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):

            eni_mac = str(
                macaddress.MAC(
                    int(macaddress.MAC(p.MAC_L_START)) + eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            self.numYields += 1
            address_map = {
                'name': 'address_map#%d' % self.numYields,
                'type': 'SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'address': eni_mac
                },
                'attributes': [
                    'SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID', '$eni#%d' % eni,
                ],
                'op': 'create',
            }

            yield address_map


if __name__ == '__main__':
    conf = AddressMaps()
    common_main(conf)
