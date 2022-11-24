#!/usr/bin/python3

import sys
import os

from dashgen.confbase import *
from dashgen.confutils import *


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            local_mac = str(macaddress.MAC(int(cp.MAC_L_START)+eni_index*int(macaddress.MAC(p.ENI_MAC_STEP)))).replace('-', ':')

            vm_underlay_dip = str(ipaddress.ip_address(p.PAL) + eni * int(ipaddress.ip_address(p.IP_STEP1)))

            acl_tables_in = []
            acl_tables_out = []

            for table_index in range(1, (p.ACL_TABLE_COUNT*2+1)):
                table_id = eni_index * 1000 + table_index

                stage = (table_index - 1) % 3 + 1
                if table_index < 4:
                    acl_tables_in.append(
                        {
                            'acl-group-id': 'acl-group-%d' % table_id,
                            'stage': stage
                        }
                    )
                else:
                    acl_tables_out.append(
                        {
                            'acl-group-id': 'acl-group-%d' % table_id,
                            'stage': stage
                        }
                    )

            self.numYields += 1
            yield {
                    #{
                        'DASH_ENI_TABLE:eni-%d' % eni : {
                            'eni_id': 'eni-%d' % eni,
                            'mac_address': local_mac,
                            'underlay_ip': vm_underlay_dip,
                            'admin_state': 'enabled',
                            'vnet': 'vnet-%d' % eni,
                            #'qos': 'qos100'
                        },
                        'OP': 'SET'
                  #  }
                    # 'acls-v4-in': acl_tables_in,
                    # 'acls-v4-out': acl_tables_out,
                    # 'route-table-v4': 'route-table-%d' % eni_index
            }


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
