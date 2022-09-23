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
        vm_underlay_dip = ipaddress.ip_address(p.PAL)

        for pa_validation_index, pa_validation in enumerate(range(p.PA_VALIDATION_START, p.PA_VALIDATION_START + p.PA_VALIDATION_COUNT)):
            vm_underlay_dip = vm_underlay_dip + int(ipaddress.ip_address(p.IP_STEP1))

            self.numYields += 1
            pa_validation_data = {
                "name": 'pa_validation#%d' % pa_validation_index,
                "type" : "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "key" : {
                    "switch_id" : "$SWITCH_ID",
                    "eni_id" : "$eni",
                    "sip" : "20.20.20.20",
                    "vni" : "1000"
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
