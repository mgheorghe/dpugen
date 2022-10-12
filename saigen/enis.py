#!/usr/bin/python3

import sys
from itertools import chain

from saigen.confbase import *
from saigen.confutils import *


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Enis ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vm_underlay_dip = ipaddress.ip_address(p.PAL) + eni_index * int(ipaddress.ip_address(p.IP_STEP1))

            self.numYields += 1
            eni_data = {
                'name': 'eni_#%d' % eni,
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_ENI',
                'attributes': [
                    'SAI_ENI_ATTR_CPS', '10000',
                    'SAI_ENI_ATTR_PPS', '100000',
                    'SAI_ENI_ATTR_FLOWS', '100000',
                    'SAI_ENI_ATTR_ADMIN_STATE', 'True',
                    'SAI_ENI_ATTR_VM_UNDERLAY_DIP', str(vm_underlay_dip),
                    'SAI_ENI_ATTR_VM_VNI', '%d' % eni,
                    'SAI_ENI_ATTR_VNET_ID', '$vnet_#%d' % eni,
                    'SAI_ENI_ATTR_INBOUND_V4_STAGE1_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V4_STAGE2_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V4_STAGE3_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V4_STAGE4_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V4_STAGE5_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V6_STAGE1_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V6_STAGE2_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V6_STAGE3_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V6_STAGE4_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_INBOUND_V6_STAGE5_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V4_STAGE1_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V4_STAGE2_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V4_STAGE3_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V4_STAGE4_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V4_STAGE5_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V6_STAGE1_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V6_STAGE2_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V6_STAGE3_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V6_STAGE4_DASH_ACL_GROUP_ID', '0',
                    'SAI_ENI_ATTR_OUTBOUND_V6_STAGE5_DASH_ACL_GROUP_ID', '0',
                ]
            }
            for stage in range(1, (p.ACL_TABLE_COUNT+1)):
                table_id = eni * 1000 + stage
                stage_index = eni_data['attributes'].index('SAI_ENI_ATTR_INBOUND_V4_STAGE%d_DASH_ACL_GROUP_ID' % stage)
                eni_data['attributes'][stage_index + 1] = '$in_acl_group_#%d' % table_id
                stage_index = eni_data['attributes'].index('SAI_ENI_ATTR_OUTBOUND_V4_STAGE%d_DASH_ACL_GROUP_ID' % stage)
                eni_data['attributes'][stage_index + 1] = '$out_acl_group_#%d' % table_id
            yield eni_data


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
