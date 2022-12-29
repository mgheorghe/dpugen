#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *

ipa = ipaddress.ip_address
maca = macaddress.MAC

class OutboundCaToPa(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Outbound CA to PA validation entry ...', file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            print("    map:eni:%d" % eni, file=sys.stderr)
            vtep_remote = ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index

            vnet_id =  eni

            for table_index in range(1, 2):
                for ip_index in range(1, 2):
                    remote_ip_a = ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP4)) + (table_index - 1) * 4 * int(ipa(p.IP_STEP3)) + (ip_index - 1) * int(ipa(p.IP_STEP2)) * 2
                    remote_mac_a = str(
                        maca(
                            int(maca(p.MAC_R_START)) +
                            eni_index * int(maca(p.ENI_MAC_STEP)) +
                            (table_index - 1) * int(maca(p.ACL_TABLE_MAC_STEP)) +
                            (ip_index - 1) * int(maca(p.ACL_POLICY_MAC_STEP)) * 2
                        )
                    ).replace('-', ':')

                    for i in range(p.IP_MAPPED_PER_ACL_RULE):
                        remote_expanded_ip = remote_ip_a + i * 2
                        remote_expanded_mac = str(
                            maca(
                                int(maca(remote_mac_a)) + i * 2
                            )
                        ).replace('-', ':')


                        self.numYields += 1
                        outbound_ca_to_pa_data = {
                            "name": "outbound_ca_to_pa_#%d" % self.numYields,
                            "op": "create",
                            "type": "SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY",
                            "key": {
                                "switch_id": "$SWITCH_ID",
                                "dst_vnet_id": "$vnet_#%d" % vnet_id,
                                "dip": str(remote_expanded_ip)
                            },
                            "attributes": [
                                "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP", str(vtep_remote),
                                "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC", remote_expanded_mac,
                                "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI", "True"
                            ]
                        }
                        yield outbound_ca_to_pa_data


if __name__ == '__main__':
    conf = OutboundCaToPa()
    common_main(conf)
