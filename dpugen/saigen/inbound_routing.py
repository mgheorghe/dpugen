#!/usr/bin/python3
"""SAI generator for Inbound Routing"""

import os
import sys

from dpugen.confbase import ConfBase, ipa
from dpugen.confutils import common_main


class InboundRouting(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            remote_ip = str(ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)))

            self.num_yields += 1
            yield {
                'name': f'inbound_routing_#eni{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'eni_id': f'$eni_#{eni}',
                    'vni': '%d' % (eni + p.ENI_L2R_STEP),
                    'sip': f'{remote_ip}',
                    'sip_mask': '255.192.0.0',
                    'priority': 0
                },
                'attributes': [
                    'SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION',       'SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE',
                    'SAI_INBOUND_ROUTING_ENTRY_ATTR_SRC_VNET_ID',  f'$vnet_#eni{eni}'
                ]
            }


if __name__ == '__main__':
    conf = InboundRouting()
    common_main(conf)
