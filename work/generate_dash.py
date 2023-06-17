import sys

sys.path.append(r'C:\github-keysight\dpugen')

from dpugen import dash

baby_hero_params = {                        # CONFIG VALUE             # DEFAULT VALUE
    'SCHEMA_VER':                      '0.0.2',

    'DC_START':                        '220.0.1.1',                # '220.0.1.2'
    'DC_STEP':                         '0.0.1.0',                  # '0.0.1.0'

    'LOOPBACK':                        '221.0.0.1',                # '221.0.0.1'
    'PAL':                             '221.1.0.1',                # '221.1.0.1'
    'PAR':                             '221.2.0.1',                # '221.2.0.1'

    'ENI_START':                        1,                         # 1
    'ENI_COUNT':                        8,                         # 64
    'ENI_MAC_STEP':                     '00:00:00:18:00:00',       # '00:00:00:18:00:00'
    'ENI_STEP':                         1,                         # 1
    'ENI_L2R_STEP':                     1,                      # 1000

    'VNET_PER_ENI':                     1,                         # 16 TODO: partialy implemented

    'MAC_L_START':                      '00:1A:C5:00:00:01',
    'MAC_R_START':                      '00:1B:6E:00:00:01',

    'IP_L_START':                       '1.1.0.1',               # local, eni
    'IP_R_START':                       '1.4.0.1',               # remote, the world

    'ACL_NSG_COUNT':                    5,                       # 5 (per direction per ENI)
    'ACL_RULES_NSG':                    10,                      # 1000
    'IP_PER_ACL_RULE':                  4,                       # 128
    # 128 (must be equal with IP_PER_ACL_RULE) TODO: not implemented
    'IP_MAPPED_PER_ACL_RULE':           4,
    'IP_ROUTE_DIVIDER_PER_ACL_RULE':    2,                       # 16 (must be 2^N)

    'ACL_NSG_MAC_STEP':                 '00:00:00:02:00:00',
    'ACL_POLICY_MAC_STEP':              '00:00:00:00:01:00',

    'IP_STEP1':                         '0.0.0.1',
    'IP_STEP_ENI':                      '0.64.0.0',
    'IP_STEP_NSG':                      '0.2.0.0',
    'IP_STEP_ACL':                      '0.0.1.0',
    'IP_STEPE':                         '0.0.0.2',
}

confgen = dash.DashConfig()

confgen.generate()


for citem in confgen.items():
    print(citem)
