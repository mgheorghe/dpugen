#!/usr/bin/python3

import math
import os
import sys

from saigen.confbase import *
from saigen.confutils import *


class OutboundRouting(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        nr_of_routes_prefixes = int(math.log(p.IP_ROUTE_DIVIDER_PER_ACL_RULE, 2))
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            print('     route:eni:%d' % eni, file=sys.stderr)

            vtep_local = p.PAL + p.IP_STEP1 * eni_index
            vtep_remote = p.PAR + p.IP_STEP1 * eni_index

            IP_L = p.IP_L_START + (eni_index - 1) * p.IP_STEP_ENI

            remote_gateway_mac = str(
                macaddress.MAC(
                    int(macaddress.MAC(p.MAC_R_START)) +
                    eni_index * int(macaddress.MAC(p.ENI_MAC_STEP))
                    #(table_index - 1) * int(macaddress.MAC(ACL_TABLE_MAC_STEP))
                )
            ).replace('-', ':')

            remote_ip = ipaddress.ip_address(p.IP_R_START) + eni_index * int(ipaddress.ip_address(p.IP_STEP_ENI))

            self.num_yields += 1
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
