#!/usr/bin/python3
"""DASH generator for Acl Groups"""

import os
import sys

from dpugen.confbase import ConfBase
from dpugen.confutils import common_main


class AclGroups(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            print(f'    acl_group:eni:{eni}', file=sys.stderr)
            for stage_in_index in range(p.ACL_NSG_COUNT):  # Per inbound stage
                table_id = eni * 1000 + stage_in_index

                self.num_yields += 1
                yield {
                    'DASH_ACL_GROUP_TABLE:%d' % table_id: {
                        'ip_version': 'ipv4',
                    },
                    'OP': 'SET'
                }

            for stage_out_index in range(p.ACL_NSG_COUNT):  # Per outbound stage
                table_id = eni * 1000 + 500 + stage_out_index

                self.num_yields += 1
                yield {
                    'DASH_ACL_GROUP_TABLE:%d' % table_id: {
                        'ip_version': 'ipv4',
                    },
                    'OP': 'SET'
                }


if __name__ == '__main__':
    conf = AclGroups()
    common_main(conf)
