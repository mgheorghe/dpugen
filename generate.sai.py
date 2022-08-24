#!/usr/bin/python3

import saigen
from saigen.confbase import *
from saigen.confutils import *

print('generating config')

parser = commonArgParser()
args = parser.parse_args()


class SaiConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__('sai-config', params)

    def generate(self):
        # Pass top-level params to sub-generrators.
        self.configs = [
            saigen.enis.Enis(self.params_dict),
            saigen.aclgroups.AclGroups(self.params_dict),
            saigen.vpcs.Vpcs(self.params_dict),
            saigen.vpcmappingtypes.VpcMappingTypes(self.params_dict),
            saigen.vpcmappings.VpcMappings(self.params_dict),
            saigen.routingappliances.RoutingAppliances(self.params_dict),
            saigen.routetables.RouteTables(self.params_dict),
            saigen.prefixtags.PrefixTags(self.params_dict),
        ]

    def toDict(self):
        return {x.dictName(): x.items() for x in self.configs}

    def items(self):
        return (c.items() for c in self.configs)


if __name__ == "__main__":
    conf = SaiConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done')
