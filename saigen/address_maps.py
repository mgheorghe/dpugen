#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class AddressMaps(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating address maps ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        vm_underlay_dip = ipaddress.ip_address(p.PAL)

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            for table_index in range(1, (p.ACL_TABLE_COUNT*2+1)):
                for ip_index in range(1, (p.ACL_RULES_NSG//2+1)):

                    remote_mac_a = str(
                        macaddress.MAC(
                            int(macaddress.MAC(p.MAC_R_START)) +
                            eni_index * int(macaddress.MAC(p.ENI_MAC_STEP)) +
                            (table_index - 1) * int(macaddress.MAC(p.ACL_TABLE_MAC_STEP)) +
                            (ip_index - 1) * int(macaddress.MAC(p.ACL_POLICY_MAC_STEP))
                        )
                    ).replace('-', ':')

                    for i in range(p.IP_MAPPED_PER_ACL_RULE):
                        remote_expanded_mac = str(
                            macaddress.MAC(
                                int(macaddress.MAC(remote_mac_a)) + i * 2
                            )
                        ).replace('-', ':')
                        self.numYields += 1
                        address_map_data_a = {
                            'name': 'address_map#%d' % self.numYields,
                            'type': 'SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY',
                            'key': {
                                'switch_id': '$SWITCH_ID',
                                'address': remote_expanded_mac
                            },
                            'attributes': [
                                'SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID', 'eni#%d' % eni,
                            ],
                            'op': 'create',
                        }

                        yield address_map_data_a

                    for i in range(p.IP_MAPPED_PER_ACL_RULE):
                        remote_expanded_mac = str(
                            macaddress.MAC(
                                int(macaddress.MAC(remote_mac_a)) + i * 2 + 1
                            )
                        ).replace('-', ':')
                        self.numYields += 1
                        address_map_data_d = {
                            'name': 'address_map#%d' % self.numYields,
                            'type': 'SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY',
                            'key': {
                                'switch_id': '$SWITCH_ID',
                                'address': remote_expanded_mac
                            },
                            'attributes': [
                                'SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID', '$eni#%d' % eni,
                            ],
                            'op': 'create',
                        }

                        yield address_map_data_d



if __name__ == '__main__':
    conf = AddressMaps()
    common_main(conf)
