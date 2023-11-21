#!/usr/bin/python3

import os
import sys
from copy import deepcopy

from dpugen.confbase import ConfBase, socket_inet_ntoa, struct_pack
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
            local_ip = ip_int.IP_L_START + eni_index * ip_int.IP_STEP_ENI
            l_ip_ac = deepcopy(str(local_ip) + '/32')
            for stage_in_index in range(p.ACL_NSG_COUNT):  # Per inbound group
                table_id = eni * 1000 + stage_in_index
                IP_R_START_stage = ip_int.IP_R_START + (eni_index * ip_int.IP_STEP_ENI) + (stage_in_index * ip_int.IP_STEP_NSG)
                for ip_index in range(0, p.ACL_RULES_NSG, 2):  # Per even ACL rule
                    remote_ip_a = IP_R_START_stage + ((ip_index // 2) * ip_int.IP_STEP_ACL)
                    ip_list_a = [socket_inet_ntoa(struct_pack('>L', remote_ip_a + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    ip_list_all = []
                    if ((stage_in_index % p.ACL_NSG_COUNT) == (p.ACL_NSG_COUNT - 1)) and (ip_index == (p.ACL_RULES_NSG - 2)):
                        all_ips_stage1 = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI + (stage_in_index + 1) * ip_int.IP_STEP_NSG
                        all_ips_stage2 = all_ips_stage1 + 1 * ip_int.IP_STEP_NSG
                        all_ips_stage3 = all_ips_stage1 + 2 * ip_int.IP_STEP_NSG
                        all_ips_stage4 = all_ips_stage1 + 3 * ip_int.IP_STEP_NSG
                        all_ips_stage5 = all_ips_stage1 + 4 * ip_int.IP_STEP_NSG
                        ip_list_all = [
                            str(all_ips_stage1) + '/15',
                            str(all_ips_stage2) + '/15',
                            str(all_ips_stage3) + '/15',
                            str(all_ips_stage4) + '/15',
                            str(all_ips_stage5) + '/15',
                        ]

                    # Allow
                    self.num_yields += 1
                    if len(ip_list_all) > 0:
                        prefixes = ip_list_a[:] + ip_list_all[:]
                    else:
                        prefixes = ip_list_a
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            'priority': ip_index,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': ','.join(prefixes),
                            'dst_addr': l_ip_ac
                        },
                        'OP': 'SET'
                    }

                    remote_ip_d = remote_ip_a - ip_int.IP_STEP1
                    ip_list_d = [socket_inet_ntoa(struct_pack('>L', remote_ip_d + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # Deny

                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'deny',
                            'terminating': 'true',
                            'src_addr': ','.join(ip_list_d),
                            'dst_addr': l_ip_ac
                        },
                        'OP': 'SET'
                    }

            for stage_out_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1000 + 500 + stage_out_index
                IP_R_START_stage = ip_int.IP_R_START + (eni_index * ip_int.IP_STEP_ENI) + (p.ACL_NSG_COUNT + stage_out_index) * ip_int.IP_STEP_NSG
                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    remote_ip_a = IP_R_START_stage + (ip_index // 2) * ip_int.IP_STEP_ACL
                    ip_list_a = [socket_inet_ntoa(struct_pack('>L', remote_ip_a + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    ip_list_all = []
                    if ((stage_out_index % p.ACL_NSG_COUNT)) == (p.ACL_NSG_COUNT - 1) and (ip_index == (p.ACL_RULES_NSG - 2)):
                        all_ips_stage1 = ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI
                        all_ips_stage2 = all_ips_stage1 + 1 * ip_int.IP_STEP_NSG
                        all_ips_stage3 = all_ips_stage1 + 2 * ip_int.IP_STEP_NSG
                        all_ips_stage4 = all_ips_stage1 + 3 * ip_int.IP_STEP_NSG
                        all_ips_stage5 = all_ips_stage1 + 4 * ip_int.IP_STEP_NSG
                        ip_list_all = [
                            str(all_ips_stage1) + '/15',
                            str(all_ips_stage2) + '/15',
                            str(all_ips_stage3) + '/15',
                            str(all_ips_stage4) + '/15',
                            str(all_ips_stage5) + '/15',
                        ]
                    # allow
                    self.num_yields += 1
                    if len(ip_list_all) > 0:
                        prefixes = ip_list_a[:] + ip_list_all[:]
                    else:
                        prefixes = ip_list_a
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            'priority': ip_index,
                            'action': 'allow',
                            'terminating': 'true',
                            'src_addr': l_ip_ac,
                            'dst_addr': ','.join(prefixes)
                        },
                        'OP': 'SET'
                    }

                    # Deny
                    remote_ip_d = remote_ip_a - ip_int.IP_STEP1
                    ip_list_d = [socket_inet_ntoa(struct_pack('>L', remote_ip_d + expanded_index * ip_int.IP_STEPE)) + '/32' for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index + 1): {
                            'priority': ip_index + 1,
                            'action': 'deny',
                            'terminating': 'true',
                            'src_addr': l_ip_ac,
                            'dst_addr': ','.join(ip_list_d)
                        },
                        'OP': 'SET'
                    }


if __name__ == '__main__':
    conf = AclRules()
    common_main(conf)
