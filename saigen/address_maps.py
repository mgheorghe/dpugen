#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class AddressMaps(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Enis ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        vm_underlay_dip = ipaddress.ip_address(p.PAL)

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            vm_underlay_dip = vm_underlay_dip + int(ipaddress.ip_address(p.IP_STEP1))

            self.numYields += 1
            address_map_data = {
                'name': 'address_map#%d' % eni_index,
                'type': 'SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY',
                'key': {
                    'switch_id': 'SWITCH_ID',
                    'address': 'ENI_MAC'
                },
                'attributes': [
                    'SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID', 'eni_id',
                ],
                'OP': 'create',
            }

            yield address_map_data


if __name__ == '__main__':
    conf = AddressMaps()
    common_main(conf)
