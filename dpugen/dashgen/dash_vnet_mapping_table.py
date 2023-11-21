#!/usr/bin/python3

import os
import sys

from dpugen.confbase import ConfBase, maca, socket_inet_ntoa, struct_pack
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
            vtep_eni = socket_inet_ntoa(struct_pack('>L', ip_int.PAL + ip_int.IP_STEP1 * eni_index))

            r_vni_id = eni + p.ENI_L2R_STEP
            remote_ip_a_eni = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI
            # 1 in 4 enis will have all its ips mapped
            if (eni % 4) == 1:
                # mapped IPs
                print(f'    mapped:eni:{eni}', file=sys.stderr)
                for nsg_index in range(p.ACL_NSG_COUNT * 2):  # Per outbound stage
                    remote_ip_a_nsg = remote_ip_a_eni + nsg_index * ip_int.IP_STEP_NSG
                    # Per half of the rules
                    for acl_index in range(p.ACL_RULES_NSG // 2):
                        remote_ip_a = remote_ip_a_nsg + acl_index * ip_int.IP_STEP_ACL
                        remote_mac_a = ip_int.MAC_R_START + eni_index * ip_int.ENI_MAC_STEP + nsg_index * ip_int.ACL_NSG_MAC_STEP + acl_index * ip_int.ACL_POLICY_MAC_STEP

                        # Allow
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):  # Per rule prefix
                            remote_expanded_ip = socket_inet_ntoa(struct_pack('>L', remote_ip_a + i * 2))
                            remote_expanded_mac = str(maca(remote_mac_a + i * 2))
                            self.num_yields += 1
                            yield {
                                'DASH_VNET_MAPPING_TABLE:vnet-%d:%s' % (r_vni_id, remote_expanded_ip): {
                                    'routing_type': 'vnet_encap',
                                    'underlay_ip': vtep_remote,
                                    'mac_address': remote_expanded_mac,
                                    'use_dst_vni': 'true'
                                },
                                'OP': 'SET'
                            }

            # 3 in 4 enis will have just mapping for gateway ip, for ip that are only routed and not mapped
            else:
                # routed IPs
                print(f'    routed:eni:{eni}', file=sys.stderr)

                remote_expanded_mac = str(maca(ip_int.MAC_R_START + eni_index * ip_int.ENI_MAC_STEP))
                self.num_yields += 1
                yield {
                    'DASH_VNET_MAPPING_TABLE:vnet-%d:%s' % (r_vni_id, vtep_eni): {
                        'routing_type': 'vnet_encap',
                        'underlay_ip': vtep_remote,
                        'mac_address': remote_expanded_mac,
                        'use_dst_vni': 'true'
                    },
                    'OP': 'SET'
                }


if __name__ == '__main__':
    conf = Mappings()
    common_main(conf)
