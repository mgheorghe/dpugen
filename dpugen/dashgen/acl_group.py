#!/usr/bin/python3

import os
import sys
from copy import deepcopy

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class AclGroups(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            local_ip = cp.IP_L_START + eni_index * cp.IP_STEP_ENI
            l_ip_ac = deepcopy(str(local_ip)+"/32")

            last_ip_index = 0
            for stage_in_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1000 + stage_in_index

                self.num_yields += 1
                yield {
                    'DASH_ACL_GROUP_TABLE:%d' % table_id: {
                        "ip_version": "ipv4",
                    },
                    'OP': 'SET'
                }

                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    # print("        %d" % ip_index)
                    rule_id_a = table_id * 10 * p.ACL_RULES_NSG + ip_index
                    remote_ip_a = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + stage_in_index * cp.IP_STEP_NSG + ip_index * cp.IP_STEP_ACL

                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE) + "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            "priority": ip_index,
                            "action": "allow",
                            "terminating": "true",
                            "src_addr": ",".join(ip_list_a[:]),
                            "dst_addr": l_ip_ac
                        },
                        'OP': 'SET'
                    }

                    rule_id_d = rule_id_a + 1
                    remote_ip_d = remote_ip_a - cp.IP_STEP1

                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # denny
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index+1): {
                            "priority": ip_index+1,
                            "action": "deny",
                            "terminating": "true",
                            "src_addr": ",".join(ip_list_d[:]),
                            "dst_addr": l_ip_ac
                        },
                        'OP': 'SET'
                    }
                    ip_index_global = ip_index

                # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
                if ((stage_in_index - 1) % p.ACL_NSG_COUNT) == 4:
                    rule_id_a = table_id * 10 * p.ACL_RULES_NSG + last_ip_index
                    all_ips_stage1 = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + stage_in_index * 4 * cp.IP_STEP_NSG
                    all_ips_stage2 = all_ips_stage1 + 1 * 4 * cp.IP_STEP_NSG
                    all_ips_stage3 = all_ips_stage1 + 2 * 4 * cp.IP_STEP_NSG
                    all_ips_stage4 = all_ips_stage1 + 3 * 4 * cp.IP_STEP_NSG
                    all_ips_stage5 = all_ips_stage1 + 4 * 4 * cp.IP_STEP_NSG
                    ip_list_all = [
                        str(all_ips_stage1)+"/14",
                        str(all_ips_stage2)+"/14",
                        str(all_ips_stage3)+"/14",
                        str(all_ips_stage4)+"/14",
                        str(all_ips_stage5)+"/14",
                    ]

                    # allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index+2): {
                            "priority": ip_index+2,
                            "action": "allow",
                            "terminating": "true",
                            "src_addr": ",".join(ip_list_all[:]),
                            "dst_addr": l_ip_ac
                        },
                        'OP': 'SET'
                    }

            for stage_out_index in range(p.ACL_NSG_COUNT):
                table_id = eni * 1500 + stage_out_index

                self.num_yields += 1
                yield {
                    'DASH_ACL_GROUP_TABLE:%d' % table_id: {
                        "ip_version": "ipv4",
                    },
                    'OP': 'SET'
                }

                rules = []
                acl_append = rules.append
                for ip_index in range(0, p.ACL_RULES_NSG, 2):
                    # print("        %d" % ip_index)
                    rule_id_a = table_id * 10 * p.ACL_RULES_NSG + ip_index
                    remote_ip_a = cp.IP_R_START + eni_index * cp.IP_STEP_ENI + \
                        (p.ACL_NSG_COUNT + stage_in_index) * cp.IP_STEP_NSG + ip_index * cp.IP_STEP_ACL

                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE) + "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index): {
                            "priority": ip_index,
                            "action": "allow",
                            "terminating": "true",
                            "src_addr": l_ip_ac,
                            "dst_addr": ",".join(ip_list_a[:])
                        },
                        'OP': 'SET'
                    }

                    rule_id_d = rule_id_a + 1
                    remote_ip_d = remote_ip_a - cp.IP_STEP1

                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) + "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]

                    # denny
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index+1): {
                            "priority": ip_index+1,
                            "action": "deny",
                            "terminating": "true",
                            "src_addr": l_ip_ac,
                            "dst_addr": ",".join(ip_list_d[:])
                        },
                        'OP': 'SET'
                    }

                # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
                if ((stage_out_index - 1) % p.ACL_NSG_COUNT) == 4:
                    rule_id_a = table_id * 10 * p.ACL_RULES_NSG + last_ip_index
                    all_ips_stage1 = cp.IP_R_START + eni_index * cp.IP_STEP_ENI
                    all_ips_stage2 = all_ips_stage1 + 1 * 4 * cp.IP_STEP_NSG
                    all_ips_stage3 = all_ips_stage1 + 2 * 4 * cp.IP_STEP_NSG
                    all_ips_stage4 = all_ips_stage1 + 3 * 4 * cp.IP_STEP_NSG
                    all_ips_stage5 = all_ips_stage1 + 4 * 4 * cp.IP_STEP_NSG
                    ip_list_all = [
                        str(all_ips_stage1)+"/14",
                        str(all_ips_stage2)+"/14",
                        str(all_ips_stage3)+"/14",
                        str(all_ips_stage4)+"/14",
                        str(all_ips_stage5)+"/14",
                    ]

                    # allow
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, ip_index+2): {
                            "priority": ip_index+2,
                            "action": "allow",
                            "terminating": "true",
                            "src_addr": l_ip_ac,
                            "dst_addr": ",".join(ip_list_all[:])
                        },
                        'OP': 'SET'
                    }


if __name__ == "__main__":
    conf = AclGroups()
    common_main(conf)
