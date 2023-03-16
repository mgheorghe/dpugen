#!/usr/bin/python3
#
# Simple example demonstrating importing of dpugen and generating a
# configuration using specified scaling parameters.
from pprint import pprint

from saigen.confbase import *
from saigen.confutils import *

import dpugen

# Constants for scale VNET outbound routing configuration
NUMBER_OF_VIP = 4
NUMBER_OF_DLE = 4
NUMBER_OF_ENI = 4
NUMBER_OF_EAM = NUMBER_OF_ENI
NUMBER_OF_ORE = 4  # Per ENI
NUMBER_OF_OCPE = 4  # Per ORE
NUMBER_OF_VNET = NUMBER_OF_ENI + (NUMBER_OF_ORE * NUMBER_OF_ENI)  # So far per ORE, but may be different
NUMBER_OF_IN_ACL_GROUP = 0
NUMBER_OF_OUT_ACL_GROUP = 0


# Scaled configuration
# Pay attention to the 'count', 'start', 'step' keywords.
# See README.md for details.
TEST_VNET_OUTBOUND_CONFIG_SCALE = {
    'DASH_VIP':                 {'vpe': {'count': NUMBER_OF_VIP, 'SWITCH_ID': '$SWITCH_ID', 'IPV4': 	{'count': NUMBER_OF_VIP, 'start': '221.0.0.2', 'step': '0.1.0.0'}}},
    'DASH_DIRECTION_LOOKUP':    {'dle': {'count': NUMBER_OF_DLE, 'SWITCH_ID': '$SWITCH_ID', 'VNI': 	{'count': NUMBER_OF_DLE, 'start': 5000, 'step': 1000}, 'ACTION': 'SET_OUTBOUND_DIRECTION'}},
    'DASH_ACL_GROUP':           {'in_acl_group_id': {'count': NUMBER_OF_IN_ACL_GROUP, 'ADDR_FAMILY': 'IPv4'}, 'out_acl_group_id': {'count': NUMBER_OF_OUT_ACL_GROUP, 'ADDR_FAMILY': 'IPv4'}},
    'DASH_VNET':                {'vnet': {'VNI': {'count': NUMBER_OF_VNET, 'start': 1000, 'step': 1000}}},
    'DASH_ENI':            {
        'name': 		{'substitution': {'base': 'eni#{0}', 'params': {0: {'start': 11, 'step': 1, 'count': NUMBER_OF_ENI, }, }, 'count': NUMBER_OF_ENI, }},
        'eni_id': 		{'increment': {'start': 11, 'step': 1, 'count': NUMBER_OF_ENI}},
        'mac_address': 	{'increment': {'start': '00:1A:C5:00:00:01', 'step': '00:00:00:18:00:00', 'count': NUMBER_OF_ENI}},
        'address': 		{'increment': {'start': '1.1.0.1', 'step': '1.0.0.0', 'count': NUMBER_OF_ENI}},
        'underlay_ip': 	{'increment': {'start': '221.0.1.1', 'step': '0.0.1.0', 'count': NUMBER_OF_ENI}},
        'vnet': 		{'substitution': {'base': 'vnet#{0}', 'params': {0: {'start': 1, 'step': 1, 'count': NUMBER_OF_ENI}, }, 'count': NUMBER_OF_ENI}},
    },
    'DASH_ENI_ETHER_ADDRESS_MAP': {'eam': {
        'count': NUMBER_OF_EAM, 'SWITCH_ID': '$SWITCH_ID',
                                             'MAC': {'count': NUMBER_OF_EAM, 'start': '00:1A:C5:00:00:01', 'step': '00:00:00:00:00:01'},
                                             'ENI_ID': {'count': NUMBER_OF_ENI, 'start': '$eni_#{0}'}
    }
    },

    'DASH_OUTBOUND_ROUTING': {
        'ore': {
            'count': NUMBER_OF_ENI * NUMBER_OF_ORE,  # Full count: OREs per ENI and VNET
            'SWITCH_ID': '$SWITCH_ID',
            'ACTION': 'ROUTE_VNET',
            'DESTINATION': 	{'count': NUMBER_OF_ORE, 'start': '1.128.0.1/9', 'step': '0.0.0.2'},
            'ENI_ID': 		{'count': NUMBER_OF_ENI, 'start': '$eni_#{0}', 'delay': NUMBER_OF_ORE},
            'DST_VNET_ID': 	{'count': NUMBER_OF_VNET, 'start': '$vnet_#{0}', 'delay': NUMBER_OF_ORE}
        }
    },

    'DASH_OUTBOUND_CA_TO_PA': {
        'ocpe': {
            'count': (NUMBER_OF_ENI * NUMBER_OF_ORE) * NUMBER_OF_OCPE, 'SWITCH_ID': '$SWITCH_ID',  # 2 Per ORE
            'DIP': {'count': NUMBER_OF_ORE * NUMBER_OF_OCPE, 'start': '1.128.0.1', 'step': '0.0.0.1'},
            'DST_VNET_ID': 	{'count': NUMBER_OF_VNET, 'start': '$vnet_#{0}', 'delay': NUMBER_OF_ORE},
            'UNDERLAY_DIP': {'count': NUMBER_OF_ENI * NUMBER_OF_ORE, 'start': '221.0.1.1', 'step': '0.0.1.0'},
            'OVERLAY_DMAC': {'count': NUMBER_OF_ENI * NUMBER_OF_ORE, 'start': '00:1B:6E:00:00:01'},
            'USE_DST_VNET_VNI': True
        }
    }
}

if __name__ == '__main__':
    # Instantiate
    conf = dpugen.sai.SaiConfig(TEST_VNET_OUTBOUND_CONFIG_SCALE)
    # Alternate way:
    # conf = dpugen.sai.SaiConfig()
    # conf.mergeParams(TEST_VNET_OUTBOUND_CONFIG_SCALE)
    conf.generate()
    print('Parameters used for generating:')
    print('===============================')
    pprint(conf.params_dict)
    print('\nGenerated configuration:')
    print('========================')
    pprint(conf.items())
