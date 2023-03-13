#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *

ipa = ipaddress.ip_address  # optimization so the . does not get executed multiple times

class PaValidation(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            eni_ip = ipa(p.IP_L_START) + eni_index * int(ipa(p.IP_STEP_ENI))

            self.num_yields += 1
            yield {
                'name': 'pa_validation_#eni%d' % eni,
                'op': 'create',
                'type' : 'SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY',
                'key' : {
                    'switch_id': '$SWITCH_ID',
                    'sip': str(eni_ip),
                    'vnet_id': '$vnet_#eni%d' % eni
                },
                'attributes' : [
                    'SAI_PA_VALIDATION_ENTRY_ATTR_ACTION', 'SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT'
                ]
            }


if __name__ == '__main__':
    conf = PaValidation()
    common_main(conf)
