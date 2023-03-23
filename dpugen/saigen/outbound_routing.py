#!/usr/bin/python3
"""SAI generator for Outbound Routing"""

import math
import os
import sys

from confbase import (
    ConfBase,
    ipa
)
from saigen.confutils import common_main


class OutboundRouting(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        nr_of_routes_prefixes = int(math.log(p.IP_ROUTE_DIVIDER_PER_ACL_RULE, 2))
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            print('     route:eni:%d' % eni, file=sys.stderr)
            vtep_eni = str(ipa(p.PAL) + int(ipa(p.IP_STEP1)) * eni_index)
            added_route_count = 0
            for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                for acl_index in range(1, (p.ACL_RULES_NSG+1)):
                    ip_map_count = 0
                    remote_ip = str(ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)) + (nsg_index - 1)
                                    * int(ipa(p.IP_STEP_NSG)) + (acl_index - 1) * int(ipa(p.IP_STEP_ACL)))
                    no_of_route_groups = p.IP_PER_ACL_RULE * 2 // p.IP_ROUTE_DIVIDER_PER_ACL_RULE
                    # for ip_index in range(0, no_of_route_groups + 1):
                    for ip_index in range(0, no_of_route_groups):
                        ip_prefix = str(ipa(remote_ip) - 1 + ip_index *
                                        p.IP_ROUTE_DIVIDER_PER_ACL_RULE * int(ipa(p.IP_STEP1)))
                        for prefix_index in range(nr_of_routes_prefixes, 0, -1):
                            nr_of_ips = 1 << (prefix_index-1)
                            mask = 32 - prefix_index + 1
                            if mask == 32:
                                ip_prefix = str(ipa(ip_prefix) + 1)

                            if (eni % 4) == 1:
                                # routes that have a mac mapping
                                self.num_yields += 1
                                yield {
                                    'name': f'outbound_routing_#eni{eni}nsg{nsg_index}acl{acl_index}ip{ip_index}p{prefix_index}',
                                    'op': 'create',
                                    'type': 'SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY',
                                    'key': {
                                        'switch_id': '$SWITCH_ID',
                                        'eni_id': f'$eni_#{eni}',
                                        'destination': f'{ip_prefix}/{mask}'
                                    },
                                    'attributes': [
                                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION', 'SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET',
                                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID', f'$vnet_#eni{eni}'
                                    ]
                                }
                                added_route_count += 1
                            else:
                                # routes that do not have a mac mapping
                                self.num_yields += 1
                                yield {
                                    'name': f'outbound_routing_#eni{eni}nsg{nsg_index}acl{acl_index}ip{ip_index}p{prefix_index}',
                                    'op': 'create',
                                    'type': 'SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY',
                                    'key': {
                                        'switch_id': '$SWITCH_ID',
                                        'eni_id': f'$eni_#{eni}',
                                        'destination': f'{ip_prefix}/{mask}'
                                    },
                                    'attributes': [
                                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION', 'SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT',
                                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID', f'$vnet_#eni{eni}',
                                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_OVERLAY_IP', vtep_eni
                                    ]
                                }
                                added_route_count += 1
                            ip_prefix = str(ipa(ip_prefix) + int(ipa(p.IP_STEP1)) * nr_of_ips)
                            ip_map_count += int(math.pow(2, (32 - mask)))
                    # TODO: transition between mapped and routed ips

            # TODO: write condition check here to add a default route if no route was added so curent ENI'
            if added_route_count == 0:
                remote_ip_prefix = str(ipa(p.IP_R_START) + eni_index * int(ipa(p.IP_STEP_ENI)))
                self.num_yields += 1
                yield {
                    'name': f'outbound_routing_#eni{eni}',
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY',
                    'key': {
                        'switch_id': '$SWITCH_ID',
                        'eni_id': f'$eni_#{eni}',
                        'destination': f'{remote_ip_prefix}/10'
                    },
                    'attributes': [
                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION', 'SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET',
                        'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID', f'$vnet_#eni{eni}'
                    ]
                }


if __name__ == '__main__':
    conf = OutboundRouting()
    common_main(conf)
