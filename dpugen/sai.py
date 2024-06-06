#!/usr/bin/python3
"""Entry point to generate a DPU Hero test config in SAI format."""
import copy
import ipaddress
import multiprocessing
import sys

import dpugen.saigen.acl_group
import dpugen.saigen.acl_rule
import dpugen.saigen.address_maps
import dpugen.saigen.direction_lookup
import dpugen.saigen.enis
import dpugen.saigen.inbound_routing
import dpugen.saigen.outbound_ca_to_pa
import dpugen.saigen.outbound_routing
import dpugen.saigen.pa_validation
import dpugen.saigen.routing_group
import dpugen.saigen.vips
import dpugen.saigen.vnets

from .confbase import (
    ConfBase,
    maca
)
from .confutils import (
    common_arg_parser,
    common_output,
    common_parse_args
)


class SaiConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)


    def generate(self):
        self.configs = [
            dpugen.saigen.vips.Vips(self.params_dict),
            dpugen.saigen.direction_lookup.DirectionLookup(self.params_dict),
            dpugen.saigen.vnets.Vnets(self.params_dict),
            dpugen.saigen.acl_group.AclGroups(self.params_dict),
            dpugen.saigen.acl_rule.AclRules(self.params_dict),
            dpugen.saigen.routing_group.RoutingGroup(self.params_dict),
            dpugen.saigen.enis.Enis(self.params_dict),
            dpugen.saigen.address_maps.Mappings(self.params_dict),
            dpugen.saigen.inbound_routing.InboundRouting(self.params_dict),
            dpugen.saigen.outbound_ca_to_pa.OutboundCaToPa(self.params_dict),
            dpugen.saigen.outbound_routing.OutboundRouting(self.params_dict),
            dpugen.saigen.pa_validation.PaValidation(self.params_dict)
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

    conf = SaiConfig()

    threads = []     
    DPUS = conf.params_dict['DPUS']

    ENI_COUNT = conf.params_dict['ENI_COUNT'] // DPUS

    for dpu_id in range(DPUS):
        print('dpu %d' % dpu_id)

        dpu_conf = copy.deepcopy(conf)
        dpu_params = {}

        dpu_params['ENI_COUNT']   = ENI_COUNT
        dpu_params['ENI_START']   = conf.params_dict['ENI_START']                                  + dpu_id * ENI_COUNT * conf.params_dict['ENI_STEP']
        dpu_params['LOOPBACK']    = str(ipaddress.ip_address(conf.params_dict['LOOPBACK'])         + dpu_id * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['PAL']         = str(ipaddress.ip_address(conf.params_dict['PAL'])              + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['PAR']         = str(ipaddress.ip_address(conf.params_dict['PAR'])              + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['GATEWAY']     = str(ipaddress.ip_address(conf.params_dict['GATEWAY'])          + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP1'])))
        dpu_params['IP_L_START']  = str(ipaddress.ip_address(conf.params_dict['IP_L_START'])       + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP_ENI'])))
        dpu_params['IP_R_START']  = str(ipaddress.ip_address(conf.params_dict['IP_R_START'])       + dpu_id * ENI_COUNT * int(ipaddress.ip_address(conf.params_dict['IP_STEP_ENI'])))
        dpu_params['MAC_L_START'] = str(maca(int(maca(conf.params_dict['MAC_L_START']))            + dpu_id * ENI_COUNT * int(maca(conf.params_dict['MAC_STEP_ENI']))))
        dpu_params['MAC_R_START'] = str(maca(int(maca(conf.params_dict['MAC_R_START']))            + dpu_id * ENI_COUNT * int(maca(conf.params_dict['MAC_STEP_ENI']))))

        dpu_params['TOTAL_OUTBOUND_ROUTES'] = conf.params_dict['TOTAL_OUTBOUND_ROUTES'] // DPUS

        threads.append(multiprocessing.Process(target=create_asic_config, args=(dpu_conf, dpu_params, 'dpu%d' % dpu_id)))
    for p in threads:                                                           
        p.start()
    for p in threads:                                                           
        p.join()

    print('done', file=sys.stderr)
