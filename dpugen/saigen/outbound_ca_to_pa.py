#!/usr/bin/python3
"""SAI generator for Outbound CA PA"""

import os
import sys

from saigen.confbase import ConfBase, ipa, maca
from saigen.confutils import common_main


class OutboundCaToPa(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):

            vtep_eni = str(ipa(p.PAL) + int(ipa(p.IP_STEP1)) * eni_index)
            vtep_remote = str(ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index)

            # 1 in 4 enis will have all its ips mapped
            if (eni % 4) == 1:
                print(f'    mapped:eni:{eni}', file=sys.stderr)
                for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                    for acl_index in range(1, (p.ACL_RULES_NSG//2+1)):
                        remote_ip_a = ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)) + (nsg_index - 1) * int(ipa(p.IP_STEP_NSG)) + (acl_index - 1) * int(ipa(p.IP_STEP_ACL))
                        remote_mac_a = str(
                            maca(
                                int(maca(p.MAC_R_START)) +
                                eni_index * int(maca(p.ENI_MAC_STEP)) +
                                (nsg_index - 1) * int(maca(p.ACL_NSG_MAC_STEP)) +
                                (acl_index - 1) * int(maca(p.ACL_POLICY_MAC_STEP))
                            )
                        ).replace('-', ':')

                        # mapping for allow ip
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = str(remote_ip_a + i * 2)
                            remote_expanded_mac = str(
                                maca(
                                    int(maca(remote_mac_a)) + i * 2
                                )
                            ).replace('-', ':')

                            self.num_yields += 1
                            yield {
                                'name': f'outbound_ca_to_pa_#eni{eni}nsg{nsg_index}acl{acl_index}i{i}A',
                                'op': 'create',
                                'type': 'SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY',
                                'key': {
                                    'switch_id': '$SWITCH_ID',
                                    'dst_vnet_id': f'$vnet_#eni{eni}',
                                    'dip': remote_expanded_ip
                                },
                                'attributes': [
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP', vtep_remote,
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC', remote_expanded_mac,
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI', 'True'
                                ]
                            }

                        # mapping for deny ip
                        # if you want to test that packets are being dropped because of the acl rule keep it
                        # if you want to test that packets are being dropped because no mapping you can comment this area
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = str(remote_ip_a + i * 2 - 1)
                            remote_expanded_mac = str(
                                maca(
                                    int(maca(remote_mac_a)) + i * 2 - 1
                                )
                            ).replace('-', ':')

                            self.num_yields += 1
                            yield {
                                'name': f'outbound_ca_to_pa_#eni{eni}nsg{nsg_index}acl{acl_index}i{i}D',
                                'op': 'create',
                                'type': 'SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY',
                                'key': {
                                    'switch_id': '$SWITCH_ID',
                                    'dst_vnet_id': f'$vnet_#eni{eni}',
                                    'dip': remote_expanded_ip
                                },
                                'attributes': [
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP', vtep_remote,
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC', remote_expanded_mac,
                                    'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI', 'True'
                                ]
                            }

            # 3 in 4 enis will have just mapping for gateway ip, for ip that are only routed and not mapped
            else:
                print(f'    routed:eni:{eni}', file=sys.stderr)

                remote_expanded_mac = str(
                    maca(
                        int(maca(p.MAC_R_START)) +
                        eni_index * int(maca(p.ENI_MAC_STEP))
                    )
                ).replace('-', ':')

                self.num_yields += 1
                yield {
                    'name': f'outbound_ca_to_pa_#eni{eni}',
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY',
                    'key': {
                        'switch_id': '$SWITCH_ID',
                        'dst_vnet_id': f'$vnet_#eni{eni}',
                        'dip': vtep_eni
                    },
                    'attributes': [
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP', vtep_remote,
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC', remote_expanded_mac,
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI', 'True'
                    ]
                }


if __name__ == '__main__':
    conf = OutboundCaToPa()
    common_main(conf)
