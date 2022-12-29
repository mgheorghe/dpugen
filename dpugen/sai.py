import saigen
from saigen.confbase import *
from saigen.confutils import *


print('generating config', file=sys.stderr)



class SaiConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def generate(self):
        # Pass top-level params to sub-generrators.
        self.configs = [
            saigen.vips.Vips(self.params_dict),
            saigen.direction_lookup.DirectionLookup(self.params_dict),
            saigen.vnets.Vnets(self.params_dict),  
            saigen.enis.Enis(self.params_dict),
            saigen.address_maps.AddressMaps(self.params_dict),
            saigen.outbound_routing.OutboundRouting(self.params_dict),
            saigen.outbound_ca_to_pa.OutboundCaToPa(self.params_dict),
            #saigen.inbound_routing.InboundRouting(self.params_dict),
            #saigen.pa_validation.PaValidation(self.params_dict),
            #saigen.acl_groups.AclGroups(self.params_dict),
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

    def write2File(self,fformat,outfile):
        writeListFileIter(self.items(), fformat, outfile)

if __name__ == '__main__':
    conf = SaiConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done', file=sys.stderr)
