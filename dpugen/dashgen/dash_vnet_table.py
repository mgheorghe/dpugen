#!/usr/bin/python3

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main
from dpugen.confutils import create_uuid_from_string


class Vnets(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            r_vni_id = p.ENI_L2R_STEP + eni
            self.num_yields += 1
            yield {
                'DASH_VNET_TABLE:vnet-%d' % r_vni_id: {
                    'vni': r_vni_id,
                    'guid': create_uuid_from_string('DASH_VNET_TABLE:vnet-%d' % r_vni_id)
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Vnets()
    common_main(conf)
