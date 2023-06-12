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

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            vtep_remote = str(ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index)
            vtep_eni = str(ipa(p.PAL) + int(ipa(p.IP_STEP1)) * eni_index)
            r_vni_id = eni + p.ENI_L2R_STEP

            # 1 in 4 enis will have all its ips mapped
            if (eni % 4) == 1:
                # mapped IPs
                print(f'    mapped:eni:{eni}', file=sys.stderr)
                for nsg_index in range(p.ACL_NSG_COUNT):  # Per outbound stage
                    for acl_index in range(p.ACL_RULES_NSG // 2):  # Per half of the rules
                        remote_ip_a = ipa(p.IP_R_START) + (eni_index * int(ipa(p.IP_STEP_ENI))) + \
                                      (nsg_index * int(ipa(p.IP_STEP_NSG))) + (acl_index * int(ipa(p.IP_STEP_ACL)))
                        remote_mac_a = str(
                            maca(
                                int(maca(p.MAC_R_START)) +
                                eni_index * int(maca(p.ENI_MAC_STEP)) +
                                nsg_index * int(maca(p.ACL_NSG_MAC_STEP)) +
                                acl_index * int(maca(p.ACL_POLICY_MAC_STEP))
                            )
                        ).replace('-', ':')

                        # Allow
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):  # Per rule prefix
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

            # 3 in 4 enis will have just mapping for gateway ip, for ip that are only routed and not mapped
            else:
                # routed IPs
                print(f'    routed:eni:{eni}', file=sys.stderr)

                remote_expanded_mac = str(
                    maca(
                        int(maca(p.MAC_R_START)) +
                        eni_index * int(maca(p.ENI_MAC_STEP))
                    )
                ).replace('-', ':')
                self.num_yields += 1
                yield {
                    "DASH_VNET_MAPPING_TABLE:vnet-%d:%s" % (r_vni_id, vtep_eni): {
                        "routing_type": "vnet_encap",
                        "underlay_ip": str(vtep_remote),
                        "mac_address": remote_expanded_mac,
                        "use_dst_vni": "true"
                    },
                    "OP": "SET"
                }


if __name__ == '__main__':
    conf = Mappings()
    common_main(conf)
