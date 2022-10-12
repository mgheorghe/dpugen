#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class OutboundRouting(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating OutboundRouting ...', file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            remote_ip = ipaddress.ip_address(p.IP_R_START) + eni_index * int(ipaddress.ip_address(p.IP_STEP4))

            self.numYields += 1
            outbound_routing_data = {
                "name": "outbound_routing_#%d" % eni,
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "$eni_#%d" % eni,
                    "destination": "%s/9" % (remote_ip)
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet_#%d" % eni
                ]
            }

            yield outbound_routing_data


if __name__ == '__main__':
    conf = OutboundRouting()
    common_main(conf)
