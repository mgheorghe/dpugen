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

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI (64)
            local_ip = cp.IP_L_START + eni_index * cp.IP_STEP_ENI
            l_ip_ac = deepcopy(str(local_ip) + '/32')
            for stage_in_index in range(p.ACL_NSG_COUNT):  # Per inbound group
                table_id = eni * 1000 + stage_in_index
                for ip_index in range(0, p.ACL_RULES_NSG, 2):  # Per even ACL rule
                    remote_ip_a = cp.IP_R_START + (eni_index * cp.IP_STEP_ENI) + (stage_in_index * cp.IP_STEP_NSG) + ((ip_index // 2) * cp.IP_STEP_ACL)
                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # Allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            'priority': ip_index,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': ','.join(ip_list_a[:]),
                            'dst_addr': l_ip_ac
                        },
                        'OP': 'SET'
                    }

                    remote_ip_d = remote_ip_a - cp.IP_STEP1
                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    if ip_index == (p.ACL_RULES_NSG - 2) and (stage_in_index % p.ACL_NSG_COUNT) == 4:
                        break  # Skip the very last rule on the last stage to have exactly 1000 rules

                    # Deny
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'deny',
                            'terminating': 'true',
                            'src_addr': ','.join(ip_list_d[:]),
                            'dst_addr': l_ip_ac
                        },
                        'OP': 'SET'
                    }

                # add as last rule in last table from ingress and egress an allow rule for all the IPs from egress and ingress
                if (stage_in_index % p.ACL_NSG_COUNT) == 4:
                    all_ips_stage1 = cp.IP_L_START + eni_index * cp.IP_STEP_ENI + stage_in_index * 4 * cp.IP_STEP_NSG
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

                    # Allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': ','.join(ip_list_all[:]),
                            'dst_addr': l_ip_ac
                        },
                        'OP': 'SET'
                    }

            for stage_out_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1000 + 500 + stage_out_index
                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    remote_ip_a = cp.IP_R_START + (eni_index * cp.IP_STEP_ENI) + (stage_out_index * cp.IP_STEP_NSG) + ((ip_index // 2) * cp.IP_STEP_ACL)
                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # Allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            'priority': ip_index,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': l_ip_ac,
                            'dst_addr': ','.join(ip_list_a[:])
                        },
                        'OP': 'SET'
                    }

                    remote_ip_d = remote_ip_a - cp.IP_STEP1
                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    if ip_index == (p.ACL_RULES_NSG - 2) and (stage_out_index % p.ACL_NSG_COUNT) == 4:
                        break  # Skip the very last rule on the last stage to have exactly 1000 rules

                    # Deny
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'deny',
                            'terminating': 'true',
                            'src_addr': l_ip_ac,
                            'dst_addr': ','.join(ip_list_d[:])
                        },
                        'OP': 'SET'
                    }

                # add as last rule in last table from ingress and egress an allow rule for all the IPs from egress and ingress
                if (stage_out_index % p.ACL_NSG_COUNT) == 4:
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

                    # Allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': l_ip_ac,
                            'dst_addr': ','.join(ip_list_all[:])
                        },
                        'OP': 'SET'
                    }


if __name__ == '__main__':
    conf = AclRules()
    common_main(conf)
