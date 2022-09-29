#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class PaValidation(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating PaValidation ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            eni_ip = ipaddress.ip_address(p.IP_L_START) + eni_index * int(ipaddress.ip_address(p.IP_STEP4))

            self.numYields += 1
            pa_validation_data = {
                "name": 'pa_validation_#%d' % eni,
                "type" : "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "key" : {
                    "switch_id" : "$SWITCH_ID",
                    "eni_id" : "$eni",
                    "sip" : str(eni_ip),
                    "vni" : eni
                },
                "attributes" : [
                    "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION", "SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT"
                ],
                'op': 'create',
            }
            yield pa_validation_data


if __name__ == '__main__':
    conf = PaValidation()
    common_main(conf)
