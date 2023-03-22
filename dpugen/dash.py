#!/usr/bin/python3
"""Entry point to generate a DPU Hero test config in DASH format."""
import sys

import dashgen.DASH_APPLIANCE_TABLE
import dashgen.DASH_ENI_TABLE
import dashgen.DASH_ROUTE_RULE_TABLE
import dashgen.DASH_ROUTE_TABLE
import dashgen.DASH_VNET_MAPPING_TABLE
import dashgen.DASH_VNET_TABLE
from dashgen.confbase import ConfBase
from dashgen.confutils import (
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
            dashgen.DASH_APPLIANCE_TABLE.Appliance(self.params_dict),
            dashgen.DASH_VNET_TABLE.Vnets(self.params_dict),
            dashgen.DASH_ENI_TABLE.Enis(self.params_dict),
            # dashgen.aclgroups.AclGroups(self.params_dict),
            # dashgen.vpcs.Vpcs(self.params_dict),
            # dashgen.vpcmappingtypes.VpcMappingTypes(self.params_dict),
            dashgen.DASH_VNET_MAPPING_TABLE.Mappings(self.params_dict),
            dashgen.DASH_ROUTE_TABLE.RouteTables(self.params_dict),
            dashgen.DASH_ROUTE_RULE_TABLE.RouteRules(self.params_dict),
            # dashgen.prefixtags.PrefixTags(self.params_dict),
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
