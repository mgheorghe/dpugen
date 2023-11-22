#!/usr/bin/python3
"""Entry point to generate a DPU Hero test config in DASH format."""
import copy
import ipaddress
import multiprocessing
import sys

import dpugen.dashgen.acl_group
import dpugen.dashgen.acl_rule
import dpugen.dashgen.dash_appliance_table
import dpugen.dashgen.dash_eni_table
import dpugen.dashgen.dash_route_rule_table
import dpugen.dashgen.dash_route_table
import dpugen.dashgen.dash_vnet_mapping_table
import dpugen.dashgen.dash_vnet_table

from .confbase import (
    ConfBase,
    maca
)
from .confutils import (
    common_arg_parser,
    common_output,
    common_parse_args
)


class DashConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def generate(self):
        # Pass top-level params to sub-generators.
        self.configs = [
            dpugen.dashgen.dash_appliance_table.Appliance(self.params_dict),
            dpugen.dashgen.dash_vnet_table.Vnets(self.params_dict),
            dpugen.dashgen.dash_eni_table.Enis(self.params_dict),
            dpugen.dashgen.acl_group.AclGroups(self.params_dict),
            dpugen.dashgen.acl_rule.AclRules(self.params_dict),
            dpugen.dashgen.dash_vnet_mapping_table.Mappings(self.params_dict),
            dpugen.dashgen.dash_route_table.OutRouteRules(self.params_dict),
            dpugen.dashgen.dash_route_rule_table.InRouteRules(self.params_dict),
        ]

    def items(self):
        result = []
        for c in self.configs:
            result.extend(c.items())
        return result

def create_asic_config(dpu_conf, dpu_params, dpu_id):
    common_parse_args(dpu_conf)
    dpu_conf.merge_params(dpu_params)
    dpu_conf.generate()
    common_output(dpu_conf, dpu_id)

if __name__ == '__main__':

    print('generating config', file=sys.stderr)
    parser = common_arg_parser()
    args = parser.parse_args()

    conf = DashConfig()

    threads = []     
    DPUS = conf.params_dict['DPUS']
    for dpu_id in range(DPUS):
        print('dpu %d' % dpu_id)

        dpu_conf = copy.deepcopy(conf)
        dpu_params = {}
        ENI_COUNT = conf.params_dict['ENI_COUNT'] // DPUS
        dpu_params['ENI_COUNT']   = ENI_COUNT
        dpu_params['ENI_START']   = conf.params_dict['ENI_START']             + dpu_id * ENI_COUNT * conf.params_dict['ENI_STEP']
        dpu_params['LOOPBACK']    = str(ipaddress.ip_address(conf.params_dict['LOOPBACK'])         + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['PAL']         = str(ipaddress.ip_address(conf.params_dict['PAL'])              + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['PAR']         = str(ipaddress.ip_address(conf.params_dict['PAR'])              + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['IP_L_START']  = str(ipaddress.ip_address(conf.params_dict['IP_L_START'])       + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP_ENI'])))
        dpu_params['IP_R_START']  = str(ipaddress.ip_address(conf.params_dict['IP_R_START'])       + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP_ENI'])))
        dpu_params['MAC_L_START'] = str(maca(int(maca(conf.params_dict['MAC_L_START'])) + dpu_id * ENI_COUNT * int(maca(conf.params_dict['MAC_STEP_ENI']))))
        dpu_params['MAC_R_START'] = str(maca(int(maca(conf.params_dict['MAC_R_START'])) + dpu_id * ENI_COUNT * int(maca(conf.params_dict['MAC_STEP_ENI']))))

        threads.append(multiprocessing.Process(target=create_asic_config, args=(dpu_conf, dpu_params, dpu_id)))

    for p in threads:                                                           
        p.start()   

    for p in threads:                                                           
        p.join()   

    print('done', file=sys.stderr)
