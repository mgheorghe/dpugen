#!/usr/bin/python3

import sys
import os

from dashgen.confbase import *
from dashgen.confutils import *


class Vnets(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            
            self.numYields += 1
            yield {
                    'DASH_VNET_TABLE:vnet-%d' % eni : {
                        'vni': eni,
                        #"guid": "659c6ce8-26ab"
                    },
                    'OP': 'SET'
            }
       
            self.numYields += 1
            r_vni_id = p.ENI_L2R_STEP + eni
            yield {
                    'DASH_VNET_TABLE:vnet-%d' % r_vni_id : {
                        'vni': r_vni_id,
                        #"guid": "659c6ce8-26ab"
                    },
                    'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Vnets()
    common_main(conf)
