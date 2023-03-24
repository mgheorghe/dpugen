#!/usr/bin/python3
"""Entry point to generate a DPU Hero test config in SAI format."""

import sys

import dpugen.saigen.acl_group
import dpugen.saigen.address_maps
import dpugen.saigen.direction_lookup
import dpugen.saigen.enis
import dpugen.saigen.inbound_routing
import dpugen.saigen.outbound_ca_to_pa
import dpugen.saigen.outbound_routing
import dpugen.saigen.pa_validation
import dpugen.saigen.vips
import dpugen.saigen.vnets

from .confbase import ConfBase
from .confutils import (
    common_arg_parser,
    common_output,
    common_parse_args,
    write_list_file_iterator
)


class SaiConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def generate(self):
        # Pass top-level params to sub-generators.
        self.configs = [
            dpugen.saigen.vips.Vips(self.params_dict),
            dpugen.saigen.direction_lookup.DirectionLookup(self.params_dict),
            dpugen.saigen.vnets.Vnets(self.params_dict),
            dpugen.saigen.acl_group.AclGroups(self.params_dict),
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

    def write_to_file(self, fformat, outfile):
        write_list_file_iterator(self.items(), fformat, outfile)


if __name__ == '__main__':

    print('generating config', file=sys.stderr)
    parser = common_arg_parser()
    args = parser.parse_args()

    conf = SaiConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done', file=sys.stderr)
