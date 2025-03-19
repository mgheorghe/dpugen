#!/usr/bin/python3
"""SAI generator for Outbound CA PA mapping table"""

import os
import sys

from dpugen.confbase import (
    ConfBase,
    maca,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class OutboundCaToPa(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            vtep_remote = socket_inet_ntoa(struct_pack('>L', ip_int.PAR + ip_int.IP_STEP1 * eni_index))
            gateway_ip =  socket_inet_ntoa(struct_pack('>L', ip_int.GATEWAY + ip_int.IP_STEP1 * eni_index))
            remote_ip_a_eni = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI
            remote_mac_a_eni = ip_int.MAC_R_START + eni_index * ip_int.MAC_STEP_ENI
            remote_expanded_mac = remote_mac_a_eni
            gateway_mac = str(maca(remote_mac_a_eni))

            # just some prefixes may have a mapping entry
            if p.ACL_MAPPED_PER_NSG >= 1:
                print(f'    mapped:eni:{eni}', file=sys.stderr)
                for nsg_index in range(p.ACL_NSG_COUNT * 2):  # Per outbound stage
                    remote_ip_a_nsg = remote_ip_a_eni + nsg_index * ip_int.IP_STEP_NSG
                    #remote_mac_a_nsg = remote_mac_a_eni + nsg_index * ip_int.MAC_STEP_NSG
                    
                    # Per half of the rules
                    for acl_index in range(p.ACL_RULES_NSG):
                        remote_ip_a = remote_ip_a_nsg + acl_index * p.IP_PER_ACL_RULE
                        #remote_mac_a = remote_mac_a_nsg + acl_index * p.IP_PER_ACL_RULE

                        if (acl_index % 2) == 0:
                            # Allow
                            if acl_index < p.ACL_MAPPED_PER_NSG:
                                for i in range(p.IP_PER_ACL_RULE):  # Per rule prefix
                                    remote_expanded_ip = socket_inet_ntoa(struct_pack('>L', remote_ip_a + i * 2))
                                    #remote_expanded_mac = str(maca(remote_mac_a + i * 2))

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
                                            'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC', str(maca(remote_expanded_mac)),
                                            'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI', 'True'
                                        ]
                                    }
                                    remote_expanded_mac =  remote_expanded_mac + 2
                            else:
                                pass

                        else:
                            # Deny
                            pass

            # some prefixes will be routed through a gateway, need mapping for gateway
            elif p.ACL_MAPPED_PER_NSG == 0:
                print(f'    routed:eni:{eni}', file=sys.stderr)

                self.num_yields += 1
                yield {
                    'name': f'outbound_ca_to_pa_#eni{eni}',
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY',
                    'key': {
                        'switch_id': '$SWITCH_ID',
                        'dst_vnet_id': f'$vnet_#eni{eni}',
                        'dip': gateway_ip
                    },
                    'attributes': [
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP', vtep_remote,
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC', gateway_mac,
                        'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI', 'True'
                    ]
                }
            
            else:
                raise Exception('ACL_MAPPED_PER_NSG <%d> cannot be < 0' % p.ACL_MAPPED_PER_NSG)


if __name__ == '__main__':
    conf = OutboundCaToPa()
    common_main(conf)
