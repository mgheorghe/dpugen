#!/usr/bin/python3

import os
import sys

from dpugen.confbase import (
    ConfBase,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class InRouteRules(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vtep_remote = socket_inet_ntoa(struct_pack('>L', ip_int.PAR + eni_index * ip_int.IP_STEP1))
            self.num_yields += 1
            yield {
                'DASH_ROUTE_RULE_TABLE:eni-%d:%d:%s/32' % (eni, 100, vtep_remote): {
                    'action_type': 'decap',
                    'priority': 0
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = InRouteRules()
    common_main(conf)
