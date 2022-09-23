#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class AclGroups(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating AclGroups ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            for stage in range(1, (p.ACL_TABLE_COUNT+1)):
                table_id = eni * 1000 + stage

                self.numYields += 1
                in_acl_group_data = {
                    'name': 'in_acl_group#%d' % table_id,
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 
                        'SAI_IP_ADDR_FAMILY_IPV4',
                    ],
                    'op': 'create',
                }
                yield in_acl_group_data

                self.numYields += 1
                in_acl_group_data = {
                    'name': 'out_acl_group#%d' % table_id,
                    'type': 'SAI_OBJECT_TYPE_DASH_ACL_GROUP',
                    'attributes': [
                        'SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY', 
                        'SAI_IP_ADDR_FAMILY_IPV4',
                    ],
                    'op': 'create',
                }
                yield in_acl_group_data


if __name__ == '__main__':
    conf = AclGroups()
    common_main(conf)
