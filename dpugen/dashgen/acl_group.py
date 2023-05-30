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

        for eni_index in range(1, p.ENI_COUNT + 1):
            local_ip = cp.IP_L_START + (eni_index - 1) * cp.IP_STEP_ENI
            l_ip_ac = deepcopy(str(local_ip)+"/32")

            for table_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                table_id = eni_index * 1000 + table_index
                self.num_yields += 1

                yield {
                        'DASH_ACL_GROUP_TABLE:%d' % table_id: {
                        "ip_version": "ipv4",
                        },
                        'OP': 'SET'
                      }
                # 
                priority_start = 1
                for ip_index in range(1, (p.ACL_RULES_NSG+1), 2):
                    remote_ip_a = cp.IP_R_START + (eni_index - 1) * cp.IP_STEP_ENI + (
                        table_index - 1) * cp.IP_STEP_NSG + (ip_index - 1) * cp.IP_STEP_ACL

                    ip_list_a = [str(remote_ip_a + expanded_index * cp.IP_STEPE) +
                                 "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]
                    ip_list_a.append(l_ip_ac)

                    self.num_yields += 1
                    yield {
                            'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, priority_start+ip_index): {
                            "priority": priority_start+ip_index,
                            "action": "allow",
                            "terminating": "false",
                            "src_addr": ",".join(ip_list_a[:]),
                            "dst_addr":  ",".join(ip_list_a[:]),
                            "dst_port": "0-0",
                            "src_port": "0-0"
                            },
                            'OP': 'SET'
                          }

                    remote_ip_d = remote_ip_a + cp.IP_STEP1
                    ip_list_d = [str(remote_ip_d + expanded_index * cp.IP_STEPE) +
                                 "/32" for expanded_index in range(0, p.IP_PER_ACL_RULE)]
                    ip_list_d.append(l_ip_ac)

                    self.num_yields += 1
                    yield {
                            'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id,priority_start+ip_index+1): {
                            "priority": priority_start+ip_index+1,
                            "action": "deny",
                            "terminating": "true",
                            "src_addr": ",".join(ip_list_d[:]),
                            "dst_addr":  ",".join(ip_list_d[:]),
                            "dst_port": "0-0",
                            "src_port": "0-0"
                            },
                            'OP': 'SET'
                          }

                # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
                if ((table_index - 1) % 3) == 2:
                    all_ipsA = cp.IP_R_START + (eni_index - 1) * cp.IP_STEP_ENI + (table_index % 6) * cp.IP_STEP_NSG
                    all_ipsB = all_ipsA + 1 * cp.IP_STEP_NSG
                    all_ipsC = all_ipsA + 2 * cp.IP_STEP_NSG

                    ip_list_all = [
                        l_ip_ac,
                        str(all_ipsA)+"/32",
                        str(all_ipsB)+"/32",
                        str(all_ipsC)+"/32",
                    ]

                    self.num_yields += 1
                    yield {
                            'DASH_ACL_RULE_TABLE:%d:rule%d' % (table_id, priority_start+ip_index+2): {
                            "priority": priority_start+ip_index+2,
                            "action": "allow",
                            "terminating": "true",
                            "src_addr": ",".join(ip_list_all[:]),
                            "dst_addr":  ",".join(ip_list_all[:]),
                            "dst_port": "0-0",
                            "src_port": "0-0"
                            },
                            'OP': 'SET'
                          }

if __name__ == "__main__":
    conf = AclGroups()
    common_main(conf)
