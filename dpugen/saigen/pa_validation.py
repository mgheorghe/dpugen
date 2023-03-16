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
            vtep_remote = str(ipa(p.PAR) + int(ipa(p.IP_STEP1)) * eni_index)

            self.num_yields += 1
            yield {
                'name': f'pa_validation_#eni{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY',
                'key': {
                    'switch_id': '$SWITCH_ID',
                    'sip': vtep_remote,
                    'vnet_id': f'$vnet_#eni{eni}'
                },
                'attributes': [
                    'SAI_PA_VALIDATION_ENTRY_ATTR_ACTION', 'SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT'
                ]
            }


if __name__ == '__main__':
    conf = PaValidation()
    common_main(conf)
