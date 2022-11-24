#!/usr/bin/python3

import sys
from copy import deepcopy
import os

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
        PAL = cp.PAL
        PAR = cp.PAR
        IP_STEP1 = cp.IP_STEP1
        IP_STEP2 = cp.IP_STEP2
        IP_STEP3 = cp.IP_STEP3
        IP_STEP4 = cp.IP_STEP4
        IP_R_START = cp.IP_R_START
        IP_L_START = cp.IP_L_START
        MAC_L_START = cp.MAC_L_START

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            PAL = PAL + IP_STEP1
            PAR = PAR + IP_STEP1

            local_ip = IP_L_START + eni_index * IP_STEP4
            local_mac = str(
                macaddress.MAC(
                    int(MAC_L_START) +
                    eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                )
            ).replace('-', ':')

            self.numYields += 1

            r_mappings = []
            r_mappings_append = r_mappings.append
            r_vni_id = eni + p.ENI_L2R_STEP
            for table_index in range(1, (p.ACL_TABLE_COUNT*2+1)):
                for ip_index in range(1, (p.ACL_RULES_NSG+1)):
                    remote_ip = IP_R_START + eni_index * IP_STEP4 + (table_index - 1) * 4 * IP_STEP3 + (ip_index - 1) * IP_STEP2
                    remote_mac = str(
                        macaddress.MAC(
                            int(macaddress.MAC(p.MAC_R_START)) +
                            eni_index * int(macaddress.MAC(p.ENI_MAC_STEP)) +
                            (table_index - 1) * int(macaddress.MAC(p.ACL_TABLE_MAC_STEP)) +
                            (ip_index - 1) * int(macaddress.MAC(p.ACL_POLICY_MAC_STEP))
                        )
                    ).replace('-', ':')

                    for i in range(p.IP_MAPPED_PER_ACL_RULE):
                        remote_expanded_ip = remote_ip + i
                        remote_expanded_mac = str(
                            macaddress.MAC(
                                int(macaddress.MAC(remote_mac)) + i
                            )
                        ).replace('-', ':')

                        self.numYields += 1
                        yield {
                            "DASH_VNET_MAPPING_TABLE:vnet-%d:%s" % (r_vni_id, remote_expanded_ip): {
                                "routing_type": "vnet_encap",
                                "underlay_ip": str(PAR),
                                "mac_address": remote_expanded_mac,
                                "use_dst_vni": "true"
                            },
                            "OP": "SET"
                        }


if __name__ == "__main__":
    conf = Mappings()
    common_main(conf)
