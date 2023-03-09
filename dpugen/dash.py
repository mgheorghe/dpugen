#!/usr/bin/python3

import dashgen
from dashgen.confbase import *
from dashgen.confutils import *

print('generating config', file=sys.stderr)

parser = commonArgParser()
args = parser.parse_args()


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
            # dashgen.DASH_ROUTE_TABLE.RouteTables(self.params_dict),
            # dashgen.DASH_ROUTE_RULE_TABLE.RouteRules(self.params_dict),
            # dashgen.prefixtags.PrefixTags(self.params_dict),
        ]

    # def toDict(self):
    #     return {x.dictName(): x.items() for x in self.configs}

    def items(self):
        result = []
        for c in self.configs:
            result.extend(c.items())
        return result
        #[c.items() for c in self.configs]
        #[].extend(c.items() for c in self.configs)

    def write2File(self, fformat, outfile):
        writeListFileIter(self.items(), fformat, outfile)

if __name__ == '__main__':
    conf = DashConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done', file=sys.stderr)
