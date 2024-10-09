#!/usr/bin/python3
"""DASH generator for QOS"""

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class Qos(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            self.num_yields += 1
            yield {
                'DASH_QOS_TABLE:qos-%d' % eni: {
                    'qos_id': 'qos-%d' % eni,
                    "bw": 0, 
                    "cps": 0, 
                    "flows": 0
                },
                'OP': 'SET'
            }

if __name__ == '__main__':
    conf = Qos()
    common_main(conf)
