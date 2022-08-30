#!/usr/bin/python3

import sys

from saigen.confbase import *
from saigen.confutils import *


class Vips(ConfBase):

    def __init__(self, params={}):
        super().__init__(params)

    def items(self):
        self.numYields = 0
        print('  Generating Vips ...', file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        vm_underlay_dip = ipaddress.ip_address(p.PAL)

        for eni_index, eni in enumerate(range(p.ENI_START, p.ENI_START + p.ENI_COUNT)):
            vm_underlay_dip = vm_underlay_dip + int(ipaddress.ip_address(p.IP_STEP1))

            self.numYields += 1
            vip_data = {
                "name": "vip_1",
                "type": "OBJECT_TYPE_VIP_ENTRY",
                "key": {
                    "SWITCH": "$switch",
                    "VIP": "$vip"
                },
                "attributes": {
                    "SAI_VIP_ENTRY_ATTR_ACTION": "SAI_VIP_ENTRY_ACTION_ACCEPT",
                },
                "OP": "create",
            }

            yield vip_data


if __name__ == '__main__':
    conf = Vips()
    common_main(conf)
