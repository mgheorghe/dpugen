#!/usr/bin/python3

import saigen
from saigen.confbase import *
from saigen.confutils import *

print('generating config')

parser = commonArgParser()
args = parser.parse_args()


class SaiConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def generate(self):
        # Pass top-level params to sub-generrators.
        self.configs = [
            saigen.vips.Vips(self.params_dict),
            saigen.direction_lookup.DirectionLookup(self.params_dict),
            saigen.acl_groups.AclGroups(self.params_dict),
            saigen.vnets.Vnets(self.params_dict),
            saigen.enis.Enis(self.params_dict),
            saigen.address_maps.AddressMaps(self.params_dict),
            saigen.inbound_routing.InboundRouting(self.params_dict),
            saigen.pa_validation.PaValidation(self.params_dict),
        ]

    # def toDict(self):
    #     return {x.dictName(): x.items() for x in self.configs}

    def items(self):
        return (c.items() for c in self.configs)


if __name__ == "__main__":
    conf = SaiConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done')
