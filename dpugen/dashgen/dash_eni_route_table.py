#!/usr/bin/python3
"""DASH generator for ENI ROUTE"""

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class EniRoute(ConfBase):

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
                'DASH_ENI_ROUTE_TABLE:eni-%d' % eni: {
                    "group_id": 'route-group-%d' % eni
                },
                "OP": "SET"
            }


if __name__ == '__main__':
    conf = EniRoute()
    common_main(conf)
