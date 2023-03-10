#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *

ipa = ipaddress.ip_address  # optimization so the . does not get executed multiple times

class InboundRouting(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params
        cp = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vtep_remote = ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index

            self.num_yields += 1
            yield {
                'name': 'inbound_routing_#%d' % eni,
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'eni_id': '%d' % eni,
                    'vni': '%d' % eni,
                    "sip": "%s" % vtep_remote,
                    "sip_mask": "255.255.255.255",
                    "priority": 0
                },
                'attributes': [
                    'SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION',
                    'SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE',
                    'SAI_INBOUND_ROUTING_ENTRY_ATTR_SRC_VNET_ID',
                    '$vnet_#%d' % eni
                ]
            }


if __name__ == '__main__':
    conf = InboundRouting()
    common_main(conf)
