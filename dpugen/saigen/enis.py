#!/usr/bin/python3
"""SAI generator for ENI"""

import os
import sys

from confbase import (
    ConfBase,
    ipa
)
from saigen.confutils import common_main


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            vm_underlay_dip = str(ipa(p.PAL) + eni_index * int(ipa(p.IP_STEP1)))

            eni_data = {
                'name': f'eni_#{eni}',
                'op': 'create',
                'type': 'SAI_OBJECT_TYPE_ENI',
                'attributes': [
                    'SAI_ENI_ATTR_CPS', '10000',
                    'SAI_ENI_ATTR_PPS', '100000',
                    'SAI_ENI_ATTR_FLOWS', '100000',
                    'SAI_ENI_ATTR_ADMIN_STATE', 'True',
                    'SAI_ENI_ATTR_VM_UNDERLAY_DIP', vm_underlay_dip,
                    'SAI_ENI_ATTR_VM_VNI', f'{eni}',
                    'SAI_ENI_ATTR_VNET_ID', f'$vnet_#eni{eni}',
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
            for nsg_index in range(1, (p.ACL_NSG_COUNT + 1)):
                stage_index = eni_data['attributes'].index(
                    f'SAI_ENI_ATTR_INBOUND_V4_STAGE{nsg_index}_DASH_ACL_GROUP_ID')
                eni_data['attributes'][stage_index + 1] = f'$in_acl_group_#eni{eni}nsg{nsg_index}'
                stage_index = eni_data['attributes'].index(
                    f'SAI_ENI_ATTR_OUTBOUND_V4_STAGE{nsg_index}_DASH_ACL_GROUP_ID')
                eni_data['attributes'][stage_index + 1] = f'$out_acl_group_#eni{eni}nsg{nsg_index}'

            self.num_yields += 1
            yield eni_data


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
