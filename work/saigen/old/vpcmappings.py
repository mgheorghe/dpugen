#!/usr/bin/python3

import sys
from copy import deepcopy

from saigen.confbase import *
from saigen.confutils import *


class VpcMappings(ConfBase):

    def __init__(self, params={}):
        super().__init__('vpc-mappings', params)

    def items(self):
        self.numYields = 0
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        PAL = cp.PAL
        PAR = cp.PAR
        IP_STEP1 = cp.IP_STEP1
        IP_STEP_ACL = cp.IP_STEP_ACL
        IP_STEP_NSG = cp.IP_STEP_NSG
        IP_STEP_ENI = cp.IP_STEP_ENI
        IP_R_START = cp.IP_R_START
        IP_L_START = cp.IP_L_START
        ACL_NSG_COUNT = p.ACL_NSG_COUNT
        ACL_RULES_NSG = p.ACL_RULES_NSG
        ENI_MAC_STEP = p.ENI_MAC_STEP
        MAC_L_START = cp.MAC_L_START
        ACL_NSG_MAC_STEP = p.ACL_NSG_MAC_STEP
        ACL_POLICY_MAC_STEP = p.ACL_POLICY_MAC_STEP
        IP_MAPPED_PER_ACL_RULE = p.IP_MAPPED_PER_ACL_RULE
        ENI_COUNT = p.ENI_COUNT
        ENI_L2R_STEP = p.ENI_L2R_STEP

        for eni_index in range(1, ENI_COUNT + 1):
            PAL = PAL + IP_STEP1
            PAR = PAR + IP_STEP1

            local_ip = IP_L_START + (eni_index - 1) * IP_STEP_ENI
            local_mac = str(
                macaddress.MAC(
                    int(MAC_L_START) +
                    (eni_index - 1) * int(macaddress.MAC(ENI_MAC_STEP))
                )
            ).replace('-', ':')

            l_vpc_mapping = deepcopy(
                {
                    "MAPPINGS:VPC:%d" % eni_index: {
                        "vpc-id": "vpc-%d" % eni_index,
                        "mappings": [
                            {
                                "routing-type": "vpc-direct",
                                "overlay-ip-address": "%s" % local_ip,
                                "underlay-ip-address": "%s" % PAL,
                                "mac": local_mac
                            }
                        ]
                    },
                }
            )
            self.numYields += 1
            yield l_vpc_mapping

            r_mappings = []
            r_mappings_append = r_mappings.append
            r_vpc = eni_index + ENI_L2R_STEP
            for table_index in range(1, (ACL_NSG_COUNT*2+1)):
                for ip_index in range(1, (ACL_RULES_NSG+1)):
                    remote_ip = IP_R_START + (eni_index - 1) * IP_STEP_ENI + (table_index - 1) * IP_STEP_NSG + (ip_index - 1) * IP_STEP_ACL
                    remote_mac = str(
                        macaddress.MAC(
                            int(macaddress.MAC('00:1B:6E:80:00:01')) +
                            (eni_index - 1) * int(macaddress.MAC(ENI_MAC_STEP)) +
                            (table_index - 1) * int(macaddress.MAC(ACL_NSG_MAC_STEP)) +
                            (ip_index - 1) * int(macaddress.MAC(ACL_POLICY_MAC_STEP))
                        )
                    ).replace('-', ':')

                    for i in range(IP_MAPPED_PER_ACL_RULE):
                        remote_expanded_ip = remote_ip + i
                        remote_expanded_mac = str(
                            macaddress.MAC(
                                int(macaddress.MAC(remote_mac)) + i
                            )
                        ).replace('-', ':')
                        r_mappings_append(
                            {
                                "routing-type": "vpc-direct",
                                "overlay-ip-address": "%s" % remote_expanded_ip,
                                "underlay-ip-address": "%s" % PAR,
                                "mac": remote_expanded_mac
                            }
                        )

            r_vpc_mapping = deepcopy(
                {
                    "MAPPINGS:VPC:%d" % r_vpc: {
                        "vpc-id": "vpc-%d" % r_vpc,
                        "mappings": r_mappings
                    },
                }
            )

            self.numYields += 1
            yield r_vpc_mapping


if __name__ == "__main__":
    conf = VpcMappings()
    common_main(conf)
