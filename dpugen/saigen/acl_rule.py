#!/usr/bin/python3

import os
import sys
from copy import deepcopy

from dpugen.confbase import (
    ConfBase,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class AclRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI (64)
            print(f'    acl:{eni}', file=sys.stderr)
            local_ip = socket_inet_ntoa(struct_pack('>L', ip_int.IP_L_START + eni_index * ip_int.IP_STEP_ENI))
            l_ip_ac = deepcopy(local_ip + '/32')

            for stage_in_index in range(p.ACL_NSG_COUNT):  # Per inbound group
                table_id = eni * 1000 + stage_in_index
                IP_R_START_stage = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI + stage_in_index * ip_int.IP_STEP_NSG
                for ip_index in range(0, p.ACL_RULES_NSG, 2):  # Per even ACL rule
                    remote_ip_a = IP_R_START_stage + ip_index * p.IP_PER_ACL_RULE
                    ip_list_a = [socket_inet_ntoa(struct_pack('>L', remote_ip_a + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    ip_list_all = []
                    if ((stage_in_index % p.ACL_NSG_COUNT) == (p.ACL_NSG_COUNT - 1)) and (ip_index == (p.ACL_RULES_NSG - 2)):
                        all_ips_stage1 = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI + (stage_in_index + 1) * ip_int.IP_STEP_NSG - 1
                        all_ips_stage2 = all_ips_stage1 + 1 * ip_int.IP_STEP_NSG
                        all_ips_stage3 = all_ips_stage1 + 2 * ip_int.IP_STEP_NSG
                        all_ips_stage4 = all_ips_stage1 + 3 * ip_int.IP_STEP_NSG
                        all_ips_stage5 = all_ips_stage1 + 4 * ip_int.IP_STEP_NSG
                        ip_list_all = [
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage1)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage2)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage3)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage4)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage5)) + '/15',
                        ]

                    # Allow
                    if len(ip_list_all) > 0:
                        prefixes = ip_list_a[:] + ip_list_all[:]
                    else:
                        prefixes = ip_list_a
                    
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$in_acl_group_#{table_id}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY', '%d' % ip_index,
                            'SAI_DASH_ACL_RULE_ATTR_ACTION', 'SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP', ','.join(prefixes),
                            'SAI_DASH_ACL_RULE_ATTR_DIP', l_ip_ac,
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL','sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT','sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT','sai_u16_range_list_t',
                        ]
                    }

                    remote_ip_d = remote_ip_a - ip_int.IP_STEP1
                    ip_list_d = [socket_inet_ntoa(struct_pack('>L', remote_ip_d + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # Deny

                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 1),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$in_acl_group_#{table_id}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY', f'{ip_index+1}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION', 'SAI_DASH_ACL_RULE_ACTION_DENY',
                            'SAI_DASH_ACL_RULE_ATTR_SIP', ','.join(ip_list_d),
                            'SAI_DASH_ACL_RULE_ATTR_DIP', l_ip_ac,
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL', 'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT', 'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT', 'sai_u16_range_list_t',
                        ]
                    }

            for stage_out_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1000 + 500 + stage_out_index
                IP_R_START_stage = ip_int.IP_R_START + (eni_index * ip_int.IP_STEP_ENI) + (p.ACL_NSG_COUNT + stage_out_index) * ip_int.IP_STEP_NSG
                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    remote_ip_a = IP_R_START_stage + ip_index * p.IP_PER_ACL_RULE
                    ip_list_a = [socket_inet_ntoa(struct_pack('>L', remote_ip_a + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    ip_list_all = []
                    if ((stage_out_index % p.ACL_NSG_COUNT)) == (p.ACL_NSG_COUNT - 1) and (ip_index == (p.ACL_RULES_NSG - 2)):
                        all_ips_stage1 = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI - 1
                        all_ips_stage2 = all_ips_stage1 + 1 * ip_int.IP_STEP_NSG
                        all_ips_stage3 = all_ips_stage1 + 2 * ip_int.IP_STEP_NSG
                        all_ips_stage4 = all_ips_stage1 + 3 * ip_int.IP_STEP_NSG
                        all_ips_stage5 = all_ips_stage1 + 4 * ip_int.IP_STEP_NSG
                        ip_list_all = [
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage1)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage2)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage3)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage4)) + '/15',
                            socket_inet_ntoa(struct_pack('>L', all_ips_stage5)) + '/15',
                        ]

                    # allow
                    if len(ip_list_all) > 0:
                        prefixes = ip_list_a[:] + ip_list_all[:]
                    else:
                        prefixes = ip_list_a
                        
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$out_acl_group_#{table_id}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY',          f'{ip_index}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION',            'SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',               l_ip_ac,
                            'SAI_DASH_ACL_RULE_ATTR_DIP',               ','.join(prefixes),
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL',          'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT',          'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT',          'sai_u16_range_list_t',
                        ]
                    }

                    # Deny
                    remote_ip_d = remote_ip_a - ip_int.IP_STEP1
                    ip_list_d = [socket_inet_ntoa(struct_pack('>L', remote_ip_d + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 1),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$out_acl_group_#{table_id}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY',          f'{ip_index+1}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION',            'SAI_DASH_ACL_RULE_ACTION_DENY',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',               l_ip_ac,
                            'SAI_DASH_ACL_RULE_ATTR_DIP',               ','.join(ip_list_d),
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL',          'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT',          'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT',          'sai_u16_range_list_t',
                        ]
                    }


if __name__ == '__main__':
    conf = AclRules()
    common_main(conf)
