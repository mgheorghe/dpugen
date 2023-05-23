#!/usr/bin/python3

import io
import os
import sys

from dpugen.confbase import (
    ConfBase,
    ipa,
    maca
)
from dpugen.confutils import common_main


class Mappings(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            debug_file = io.open('macs_for_eni_%d.txt' % eni, "wt")
            # vtep_local = cp.PAL + eni_index * cp.IP_STEP1
            #vtep_remote = cp.PAR + eni_index * cp.IP_STEP1
            vtep_remote = str(ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index)

            r_vni_id = eni + p.ENI_L2R_STEP
            # 1 in 4 enis will have all its ips mapped
            if (eni % 4) == 1:
                # mapped IPs
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

                        debug_file.write('############ ALLOW\n')
                        # mapping for deny ip
                        # if you want to test that packets are being dropped because of the acl rule keep it
                        # if you want to test that packets are being dropped because no mapping you can comment this area
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = str(remote_ip_a + i * 2)
                            remote_expanded_mac = str(
                                maca(
                                    int(maca(remote_mac_a)) + i * 2
                                )
                            ).replace('-', ':')

                            self.num_yields += 1
                            yield {
                                "DASH_VNET_MAPPING_TABLE:vnet-%d:%s" % (r_vni_id, remote_expanded_ip): {
                                    "routing_type": "vnet_encap",
                                    "underlay_ip": str(vtep_remote),
                                    "mac_address": remote_expanded_mac,
                                    "use_dst_vni": "true"
                                },
                                "OP": "SET"
                            }
                            debug_file.write(remote_expanded_mac + '\n')

                        debug_file.write('############ DENNY\n')
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = str(remote_ip_a + i * 2 -1)
                            remote_expanded_mac = str(
                                maca(
                                    int(maca(remote_mac_a)) + i * 2 - 1
                                )
                            ).replace('-', ':')

                            self.num_yields += 1
                            yield {
                                "DASH_VNET_MAPPING_TABLE:vnet-%d:%s" % (r_vni_id, remote_expanded_ip): {
                                    "routing_type": "vnet_encap",
                                    "underlay_ip": str(vtep_remote),
                                    "mac_address": remote_expanded_mac,
                                    "use_dst_vni": "true"
                                },
                                "OP": "SET"
                            }
                            debug_file.write(remote_expanded_mac + '\n')

            # 3 in 4 enis will have just mapping for gateway ip, for ip that are only routed and not mapped
            else:
                # routed IPs
                print(f'    routed:eni:{eni}', file=sys.stderr)
                remote_expanded_ip = cp.IP_R_START + eni_index * cp.IP_STEP_ENI

                remote_expanded_mac = str(
                    maca(
                        int(maca(p.MAC_R_START)) +
                        eni_index * int(maca(p.ENI_MAC_STEP))
                    )
                ).replace('-', ':')
                self.num_yields += 1
                yield {
                    "DASH_VNET_MAPPING_TABLE:vnet-%d:%s" % (r_vni_id, remote_expanded_ip): {
                        "routing_type": "vnet_encap",
                        "underlay_ip": str(vtep_remote),
                        "mac_address": remote_expanded_mac,
                        "use_dst_vni": "true"
                    },
                    "OP": "SET"
                }
                debug_file.write(remote_expanded_mac + '\n')
            debug_file.close()


if __name__ == '__main__':
    conf = Mappings()
    common_main(conf)
