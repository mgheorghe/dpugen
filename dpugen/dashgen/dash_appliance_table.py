#!/usr/bin/python3

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class Appliance(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        # for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
        #     self.num_yields += 1
        #     yield {
        #         'DASH_APPLIANCE_TABLE:appliance-%d' % eni: {
        #             "sip": "221.0.0.1",
        #             "vm_vni": f'{eni}'
        #         },
        #         'OP': 'SET'
        #     }
        self.num_yields += 1
        yield {
            'DASH_APPLIANCE_TABLE:appliance-%d' % p.ENI_START: {
                'sip': f'{p.LOOPBACK}',
                'vm_vni': p.ENI_START,
                'local_region_id': 100,
                'trusted_vnis_list': [
                    {
                        'range': {
                            'min': 100,
                            'max': 100
                        }
                    },
                    {
                        'range': {
                            'min': 250,
                            'max': 511
                        }
                    }
                ]
            },
            'OP': 'SET'
        }
        # yield {
        #     "DASH_ROUTING_TYPE_TABLE:vnet": {
        #         "action_name": 'action-%d' % p.ENI_START,
        #         "action_type": "maprouting"
        #     },
        #     "OP": "SET"
        # }
        # yield {
        #     "DASH_ROUTING_TYPE_TABLE:vnet_direct": {
        #         "action_name": 'action-%d' % p.ENI_START,
        #         "action_type": "maprouting"
        #     },
        #     "OP": "SET"
        # }
        # yield {
        #     "DASH_ROUTING_TYPE_TABLE:direct": {"action_name": "action-1000", "action_type": "direct"}, 
        #     "OP": "SET"
        # }
        # yield {
        #     "DASH_ROUTING_TYPE_TABLE:vnet_encap": {
        #         "action_name": 'action-%d' % p.ENI_START,
        #         "action_type": "staticencap",
        #         "encap_type": "vxlan"
        #     },
        #     "OP": "SET"
        # }
        yield {
            "DASH_ROUTING_TYPE_TABLE:privatelink": [
                {
                    "action_name": 'action-1',
                    "action_type": "4_to_6"
                },
                {
                    "action_name": 'action-2',
                    "action_type": "staticencap",
                    "encap_type": "nvgre",
                    "vni": 100
                }
            ],
            "OP": "SET"
        }




if __name__ == '__main__':
    conf = Appliance()
    common_main(conf)
