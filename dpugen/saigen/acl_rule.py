#!/usr/bin/python3

import os
import sys
from copy import deepcopy

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class AclRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            local_ip = cp.IP_L_START + eni_index * cp.IP_STEP_ENI
            l_ip_ac = deepcopy(str(local_ip) + '/32')

            for stage_in_index in range(p.ACL_NSG_COUNT):
                nsg_index = stage_in_index + 1
                table_id = eni * 1000 + stage_in_index

                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    # print("        %d" % ip_index)
                    remote_ip_a = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + stage_in_index * cp.IP_STEP_NSG + ip_index * cp.IP_STEP_ACL

                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE)
                                 + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # allow
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$in_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY','%d' % ip_index,
                            'SAI_DASH_ACL_RULE_ATTR_ACTION','SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',','.join(ip_list_a[:]),
                            'SAI_DASH_ACL_RULE_ATTR_DIP',l_ip_ac,
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL','sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT','sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT','sai_u16_range_list_t',
                        ]
                    }

                    remote_ip_d = remote_ip_a - cp.IP_STEP1

                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # denny
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 1),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$in_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY', f'{ip_index+1}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION', 'SAI_DASH_ACL_RULE_ACTION_DENY',
                            'SAI_DASH_ACL_RULE_ATTR_SIP', ','.join(ip_list_d[:]),
                            'SAI_DASH_ACL_RULE_ATTR_DIP', l_ip_ac,
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL', 'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT', 'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT', 'sai_u16_range_list_t',
                        ]
                    }

                # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
                if (stage_in_index % p.ACL_NSG_COUNT) == (p.ACL_NSG_COUNT - 1):
                    all_ips_stage1 = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + (stage_in_index + 1) * cp.IP_STEP_NSG
                    all_ips_stage2 = all_ips_stage1 + 1 * cp.IP_STEP_NSG
                    all_ips_stage3 = all_ips_stage1 + 2 * cp.IP_STEP_NSG
                    all_ips_stage4 = all_ips_stage1 + 3 * cp.IP_STEP_NSG
                    all_ips_stage5 = all_ips_stage1 + 4 * cp.IP_STEP_NSG
                    ip_list_all = [
                        str(all_ips_stage1) + '/14',
                        str(all_ips_stage2) + '/14',
                        str(all_ips_stage3) + '/14',
                        str(all_ips_stage4) + '/14',
                        str(all_ips_stage5) + '/14',
                    ]

                    # allow
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 2),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$in_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY', f'{ip_index + 2}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION', 'SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP', ','.join(ip_list_all[:]),
                            'SAI_DASH_ACL_RULE_ATTR_DIP', l_ip_ac,
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL', 'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT', 'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT', 'sai_u16_range_list_t',
                        ]
                    }

            for stage_out_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1000 + 500 + stage_out_index

                rules = []
                acl_append = rules.append
                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    # print("        %d" % ip_index)
                    remote_ip_a = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + \
                        (p.ACL_NSG_COUNT + stage_out_index) * cp.IP_STEP_NSG + ip_index * cp.IP_STEP_ACL

                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE)
                                 + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # allow
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$out_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY',          f'{ip_index}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION',            'SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',               l_ip_ac,
                            'SAI_DASH_ACL_RULE_ATTR_DIP',               ','.join(ip_list_a[:]),
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL',          'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT',          'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT',          'sai_u16_range_list_t',
                        ]
                    }

                    remote_ip_d = remote_ip_a - cp.IP_STEP1

                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # denny
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 1),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$out_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY',          f'{ip_index+1}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION',            'SAI_DASH_ACL_RULE_ACTION_DENY',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',               l_ip_ac,
                            'SAI_DASH_ACL_RULE_ATTR_DIP',               ','.join(ip_list_d[:]),
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL',          'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT',          'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT',          'sai_u16_range_list_t',
                        ]
                    }

                # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
                if (stage_out_index % p.ACL_NSG_COUNT) == (p.ACL_NSG_COUNT - 1):
                    all_ips_stage1 = cp.IP_R_START + eni_index * cp.IP_STEP_ENI
                    all_ips_stage2 = all_ips_stage1 + 1 * 4 * cp.IP_STEP_NSG
                    all_ips_stage3 = all_ips_stage1 + 2 * 4 * cp.IP_STEP_NSG
                    all_ips_stage4 = all_ips_stage1 + 3 * 4 * cp.IP_STEP_NSG
                    all_ips_stage5 = all_ips_stage1 + 4 * 4 * cp.IP_STEP_NSG
                    ip_list_all = [
                        str(all_ips_stage1) + '/14',
                        str(all_ips_stage2) + '/14',
                        str(all_ips_stage3) + '/14',
                        str(all_ips_stage4) + '/14',
                        str(all_ips_stage5) + '/14',
                    ]

                    # allow
                    self.num_yields += 1
                    yield {
                        'name': 'dash_acl_%d_rule_%d' % (table_id, ip_index + 2),
                        'op': 'create',
                        'type': 'SAI_OBJECT_TYPE_DASH_ACL_RULE',
                        'attributes': [
                            'SAI_DASH_ACL_RULE_ATTR_DASH_ACL_GROUP_ID', f'$out_acl_group_#eni{eni}nsg{nsg_index}',
                            'SAI_DASH_ACL_RULE_ATTR_PRIORITY',          f'{ip_index+2}',
                            'SAI_DASH_ACL_RULE_ATTR_ACTION',            'SAI_DASH_ACL_RULE_ACTION_PERMIT',
                            'SAI_DASH_ACL_RULE_ATTR_SIP',               l_ip_ac,
                            'SAI_DASH_ACL_RULE_ATTR_DIP',               ','.join(ip_list_all[:]),
                            # 'SAI_DASH_ACL_RULE_ATTR_PROTOCOL',          'sai_u8_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_SRC_PORT',          'sai_u16_range_list_t',
                            # 'SAI_DASH_ACL_RULE_ATTR_DST_PORT',          'sai_u16_range_list_t',
                        ]
                    }


if __name__ == '__main__':
    conf = AclRules()
    common_main(conf)
