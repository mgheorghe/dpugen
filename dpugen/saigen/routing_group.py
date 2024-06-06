#!/usr/bin/python3
"""SAI generator for ENI"""

import os
import sys

from dpugen.confbase import (
    ConfBase,
    maca,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class RoutingGroup(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI

            routing_group_data = {
                'name': f'routinggid_#{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_ROUTING_GROUP',
                'attributes': [
                    'SAI_ROUTING_GROUP_ATTR_ADMIN_STATE', 'True',
                ]
            }

            self.num_yields += 1
            yield routing_group_data


if __name__ == '__main__':
    conf = RoutingGroup()
    common_main(conf)
