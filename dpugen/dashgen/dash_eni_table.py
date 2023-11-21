#!/usr/bin/python3

import os
import sys

from dpugen.confbase import ConfBase, maca, socket_inet_ntoa, struct_pack
from dpugen.confutils import common_main


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            local_mac = str(maca(int(ip_int.MAC_L_START) + eni_index * int(maca(p.ENI_MAC_STEP))))
            vm_underlay_dip = socket_inet_ntoa(struct_pack('>L', ip_int.PAL + eni_index * ip_int.IP_STEP1))
            r_vni_id = p.ENI_L2R_STEP + eni
            for nsg_index in range(p.ACL_NSG_COUNT * 2):
                stage = nsg_index % p.ACL_NSG_COUNT + 1
                if nsg_index < p.ACL_NSG_COUNT:
                    nsg_id = eni * 1000 + nsg_index
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_IN_TABLE:eni-%d:%d' % (eni, stage): {
                            'acl_group_id': f'{nsg_id}'
                        },
                        'OP': 'SET'
                    }

                else:
                    nsg_id = eni * 1000 + 500 + nsg_index - p.ACL_NSG_COUNT
                    self.num_yields += 1
                    yield {
                        'DASH_ACL_OUT_TABLE:eni-%d:%d' % (eni, stage): {
                            'acl_group_id': f'{nsg_id}'
                        },
                        'OP': 'SET'
                    }

            self.num_yields += 1
            yield {
                'DASH_ENI_TABLE:eni-%d' % eni: {
                    'eni_id': 'eni-%d' % eni,
                    'mac_address': local_mac,
                    'underlay_ip': vm_underlay_dip,
                    'admin_state': 'enabled',
                    'vnet': 'vnet-%d' % r_vni_id,
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
