#!/usr/bin/python3
"""DASH generator for Outbound CA PA mapping table"""

import os
import sys

from dpugen.confbase import (
    ConfBase,
    maca,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class Mappings(ConfBase):

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
            gateway_mac = str(maca(remote_mac_a_eni))

            # add mapping for ENI itself SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY
            eni_ip = socket_inet_ntoa(struct_pack('>L', ip_int.IP_L_START + eni_index * ip_int.IP_STEP_ENI))
            eni_mac = str(maca(ip_int.MAC_L_START + eni_index * ip_int.MAC_STEP_ENI))
            r_vni_id = eni + p.ENI_L2R_STEP
            
            self.num_yields += 1
            yield {
                'DASH_VNET_MAPPING_TABLE:vnet-%d:%s' % (r_vni_id, eni_ip): {
                    'routing_type': 'vnet_encap',
                    'underlay_ip': p.LOOPBACK,
                    'mac_address': eni_mac,
                    'use_dst_vni': 'true'
                },
                'OP': 'SET'
            }

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
                            if acl_index <= p.ACL_MAPPED_PER_NSG:
                                for i in range(p.IP_PER_ACL_RULE):  # Per rule prefix
                                    remote_expanded_ip = socket_inet_ntoa(struct_pack('>L', remote_ip_a + i * 2))
                                    #remote_expanded_mac = str(maca(remote_mac_a + i * 2))

                                    self.num_yields += 1
                                    yield {
                                        'DASH_VNET_MAPPING_TABLE:vnet-%d:%s' % (r_vni_id, remote_expanded_ip): {
                                            'routing_type': 'vnet_encap',
                                            'underlay_ip': vtep_remote,
                                            'mac_address': str(maca(remote_mac_a_eni)),
                                            'use_dst_vni': 'true'
                                        },
                                        'OP': 'SET'
                                    }
                                    remote_mac_a_eni = remote_mac_a_eni + 2
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
                    'DASH_VNET_MAPPING_TABLE:vnet-%d:%s' % (r_vni_id, gateway_ip): {
                        'routing_type': 'vnet_encap',
                        'underlay_ip': vtep_remote,
                        'mac_address': gateway_mac,
                        'use_dst_vni': 'true'
                    },
                    'OP': 'SET'
                }
            
            else:
                raise Exception('ACL_MAPPED_PER_NSG <%d> cannot be < 0' % p.ACL_MAPPED_PER_NSG)


if __name__ == '__main__':
    conf = Mappings()
    common_main(conf)
