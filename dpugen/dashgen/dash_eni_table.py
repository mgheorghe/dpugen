#!/usr/bin/python3
"""DASH generator for ENI"""

import os
import sys

from dpugen.confbase import (
    ConfBase,
    maca,
    socket_inet_ntoa,
    struct_pack
)
from dpugen.confutils import common_main


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)
        self.num_yields = 0

    def dec2hex(self, dec):
        hex_str = hex(dec)[2:]
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        return hex_str

    def hex2lehex(self, hex_str):
        # Convert hex string to little-endian hex string
        le_hex_str = ''.join(reversed([hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]))
        return le_hex_str

    def get_pl_sip_encoding(self, vni):
        # "::e903:64:ff71:0:0/::ffff:ffff:ffff:0:0"
        # 64 -> local region id 100 dec, in hex is 64 -> Hardcoded
        # d107->  07d1 -> vnet vni: dec 2001 = hex 07d1 = little endian d107
        # ff71 -> 71ff -> subnet label coming from ENI -> 29183  -> Hardcoded

        vni_hex_le = self.hex2lehex(self.dec2hex(vni))
        return "::%s:64:ff71:0:0/::ffff:ffff:ffff:0:0" % vni_hex_le

    def items(self):
        print('  Generating %s ...' % os.path.basename(__file__), file=sys.stderr)
        p = self.params
        ip_int = self.cooked_params

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT * p.ENI_STEP, p.ENI_STEP)):  # Per ENI
            local_mac = str(maca(ip_int.MAC_L_START + eni_index * ip_int.MAC_STEP_ENI))
            vm_underlay_dip = socket_inet_ntoa(struct_pack('>L', ip_int.PAL + eni_index * ip_int.IP_STEP1))
            pl_underlay_sip = socket_inet_ntoa(struct_pack('>L', ip_int.PAL + eni_index * ip_int.IP_STEP1 + 256))
            pl_sip_encoding = self.get_pl_sip_encoding(eni)
            r_vni_id = p.ENI_L2R_STEP + eni
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
                'DASH_QOS_TABLE:qos-%d' % eni: {
                    'qos_id': 'qos-%d' % eni,
                    "bw": 0, 
                    "cps": 0, 
                    "flows": 0
                },
                'OP': 'SET'
            }

            self.num_yields += 1
            yield {
                'DASH_ENI_TABLE:eni-%d' % eni: {
                    'eni_id': 'eni-%d' % eni,
                    "qos": 'qos-%d' % eni,
                    'mac_address': local_mac,
                    'underlay_ip': vm_underlay_dip,
                    'admin_state': 'enabled',
                    'vnet': 'vnet-%d' % r_vni_id,
                    "pl_underlay_sip": pl_underlay_sip,
                    "pl_sip_encoding": pl_sip_encoding,
                },
                'OP': 'SET'
            }


if __name__ == '__main__':
    conf = Enis()
    common_main(conf)
