#!/usr/bin/python3
"""SAI generator for Acl Groups"""

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

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            for nsg_index in range(1, (p.ACL_NSG_COUNT+1)):

                self.num_yields += 1
                yield {
                    'name': f'in_acl_group_#eni{eni}nsg{nsg_index}',
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 'SAI_IP_ADDR_FAMILY_IPV4',
                    ]
                }

                self.num_yields += 1
                yield {
                    'name': f'out_acl_group_#eni{eni}nsg{nsg_index}',
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 'SAI_IP_ADDR_FAMILY_IPV4',
                    ]
                }


if __name__ == '__main__':
    conf = AclGroups()
    common_main(conf)
