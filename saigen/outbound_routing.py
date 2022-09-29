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

        for ore_index, ore in enumerate(range(p.OUTBOUND_ROUTING_START, p.OUTBOUND_ROUTING_START + p.OUTBOUND_ROUTING_COUNT)):

            self.numYields += 1
            ore_data = {
                "name": "ore#%d" % ore_index,
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "$eni",
                    "destination": "10.1.0.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet"
                ]
            }

            yield ore_data


if __name__ == '__main__':
    conf = OutboundRouting()
    common_main(conf)
