#!/usr/bin/python3

import os
import sys

from saigen.confbase import *
from saigen.confutils import *


class AclGroups(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        self.num_yields = 0
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            for stage in range(1, (p.ACL_NSG_COUNT+1)):
                table_id = eni * 1000 + stage

                self.num_yields += 1
                yield {
                    'name': 'in_acl_group_#%d' % table_id,
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 'SAI_IP_ADDR_FAMILY_IPV4',
                    ]
                }

                self.num_yields += 1
                yield {
                    'name': 'out_acl_group_#%d' % table_id,
                    'op': 'create',
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 'SAI_IP_ADDR_FAMILY_IPV4',
                    ]
                }


if __name__ == '__main__':
    conf = AclGroups()
    common_main(conf)
