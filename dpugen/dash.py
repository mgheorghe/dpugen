#!/usr/bin/python3
"""Entry point to generate a DPU Hero test config in DASH format."""
import sys

import dpugen.dashgen.acl_group
import dpugen.dashgen.dash_appliance_table
import dpugen.dashgen.dash_eni_table
import dpugen.dashgen.dash_route_rule_table
import dpugen.dashgen.dash_route_table
import dpugen.dashgen.dash_vnet_mapping_table
import dpugen.dashgen.dash_vnet_table

from .confbase import ConfBase
from .confutils import (
    common_arg_parser,
    common_output,
    common_parse_args,
    write_list_file_iterator
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
            # dashgen.vpc.Vpcs(self.params_dict),
            # dashgen.vpcmappingtypes.VpcMappingTypes(self.params_dict),
            dpugen.dashgen.dash_vnet_mapping_table.Mappings(self.params_dict),
            dpugen.dashgen.dash_route_table.RouteTables(self.params_dict),
            dpugen.dashgen.dash_route_rule_table.RouteRules(self.params_dict),
            # dashgen.prefix_tag.PrefixTags(self.params_dict),
        ]

    def items(self):
        result = []
        for c in self.configs:
            result.extend(c.items())
        return result

    def write_to_file(self, fformat, outfile):
        write_list_file_iterator(self.items(), fformat, outfile)


if __name__ == '__main__':

    print('generating config', file=sys.stderr)
    parser = common_arg_parser()
    args = parser.parse_args()

    conf = DashConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done', file=sys.stderr)
