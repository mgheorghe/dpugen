#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class OutboundCaToPa(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Outbound CA to PA validation entry ...', file=sys.stderr)
        p = self.params

        for ocp_index, ocp in enumerate(range(p.OUTBOUND_CA_TO_PA_START, p.OUTBOUND_CA_TO_PA_START + p.OUTBOUND_CA_TO_PA_COUNT)):

            self.numYields += 1
            ocp_data = {
                "name": "ocpe#%d" % ocp_index,
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "dst_vnet_id": "$vnet",
                    "dip": "10.1.2.50"
                },
                "attributes": [
                    "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP", "172.16.1.20",
                    "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC", "00:DD:DD:DD:DD:DD",
                    "SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNET_VNI", "True"
                ]
            }
            yield ocp_data


if __name__ == '__main__':
    conf = OutboundCaToPa()
    common_main(conf)
