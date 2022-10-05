import pytest
import saigen
from saigen.confbase import ConfBase


@pytest.fixture(scope="session")
def confgen():

    class SaiConfig(ConfBase):

        def generate(self):
            # Pass top-level params to sub-generators.
            self.configs = [
                saigen.vips.Vips(self.params_dict),
                saigen.direction_lookup.DirectionLookup(self.params_dict),
                saigen.acl_groups.AclGroups(self.params_dict),
                saigen.vnets.Vnets(self.params_dict),
                saigen.enis.Enis(self.params_dict),
                saigen.address_maps.AddressMaps(self.params_dict),
                saigen.outbound_routing.OutboundRouting(self.params_dict),
                saigen.outbound_ca_to_pa.OutboundCaToPa(self.params_dict),
                # saigen.inbound_routing.InboundRouting(self.params_dict),
                # saigen.pa_validation.PaValidation(self.params_dict),
            ]

        def items(self, reverse=False):
            result = []
            for c in self.configs:
                result.extend(c.items())
            return result

    return SaiConfig()
