#!/usr/bin/python3

import os
import sys

from dashgen.confbase import (
    ConfBase,
    ipa,
    maca
)
from dashgen.confutils import common_main


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.num_yields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):
            local_mac = str(maca(int(cp.MAC_L_START)+eni_index*int(maca(p.ENI_MAC_STEP)))).replace('-', ':')
            vm_underlay_dip = str(ipa(p.PAL) + eni_index * int(ipa(p.IP_STEP1)))

            acl_nsgs_in = []
            acl_nsgs_out = []

            for nsg_index in range(1, (p.ACL_NSG_COUNT*2+1)):
                nsg_id = eni_index * 1000 + nsg_index

                stage = (nsg_index - 1) % 3 + 1
                if nsg_index < 4:
                    acl_nsgs_in.append(
                        {
                            'acl-group-id': 'acl-group-%d' % nsg_id,
                            'stage': stage
                        }
                    )
                else:
                    acl_nsgs_out.append(
                        {
                            'acl-group-id': 'acl-group-%d' % nsg_id,
                            'stage': stage
                        }
                    )

            self.num_yields += 1
            yield {
                'DASH_ENI_NSG:eni-%d' % eni: {
                    'eni_id': 'eni-%d' % eni,
                    'mac_address': local_mac,
                    'underlay_ip': vm_underlay_dip,
                    'admin_state': 'enabled',
                    'vnet': 'vnet-%d' % eni,
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
