#!/usr/bin/python3

import os
import sys
from copy import deepcopy
import io

from dashgen.confbase import *
from dashgen.confutils import *


class Mappings(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            debug_file = io.open('macs_for_eni_%d.txt' % eni, "wt")
            vtep_local = cp.PAL + eni_index * cp.IP_STEP1
            vtep_remote = cp.PAR + eni_index * cp.IP_STEP1

            local_ip = cp.IP_L_START + eni_index * cp.IP_STEP_ENI
            local_mac = str(
                macaddress.MAC(
                    int(macaddress.MAC(p.MAC_L_START)) +
                    eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            self.numYields += 1

            r_mappings = []
            r_mappings_append = r_mappings.append
            r_vni_id = eni + p.ENI_L2R_STEP

            if (eni % 4) == 1:
                # mapped IPs

                for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                    for ip_index in range(1, (p.ACL_RULES_NSG//2+1)):
                        remote_ip_a = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + (nsg_index - 1) * cp.IP_STEP_NSG + (ip_index - 1) * cp.IP_STEP_ACL
                        remote_mac_a = str(
                            macaddress.MAC(
                                int(macaddress.MAC(p.MAC_R_START)) +
                                eni_index * int(macaddress.MAC(p.ENI_MAC_STEP)) +
                                (nsg_index - 1) * int(macaddress.MAC(p.ACL_NSG_MAC_STEP)) +
                                (ip_index - 1) * int(macaddress.MAC(p.ACL_POLICY_MAC_STEP))
                            )
                        ).replace('-', ':')

                        debug_file.write('############ ALLOW\n')
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = remote_ip_a + i * 2
                            remote_expanded_mac = str(
                                macaddress.MAC(
                                    int(macaddress.MAC(remote_mac_a)) + i * 2
                                )
                            ).replace('-', ':')

                            self.numYields += 1
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

                        remote_ip_d = remote_ip_a - 1
                        debug_file.write('############ DENNY\n')
                        for i in range(p.IP_MAPPED_PER_ACL_RULE):
                            remote_expanded_ip = remote_ip_d + i * 2
                            remote_expanded_mac = str(
                                macaddress.MAC(
                                    int(macaddress.MAC(remote_mac_a)) + i * 2 - 1
                                )
                            ).replace('-', ':')

                            self.numYields += 1
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
            else:
                # routed IPs

                remote_expanded_mac = str(
                    macaddress.MAC(
                        int(macaddress.MAC(p.MAC_R_START)) +
                        eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                    )
                ).replace('-', ':')

                self.numYields += 1
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
