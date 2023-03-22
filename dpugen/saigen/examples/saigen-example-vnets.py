#!/usr/bin/python3
#
# Simple example demonstrating importing of dpugen and generating vnets only.
from pprint import pprint

from saigen.confbase import ConfBase
from saigen.confutils import common_main
from saigen.vnets import *

if __name__ == '__main__':
    # Override a few params.
    # See saigen.dflt_params.py for complete list
    params = {
        'ENI_COUNT':                        16,
        'ENI_START':                        10000,
        'ENI_STEP':                         1000,
        'VNET_PER_ENI':                     4
    }

    # Instantiate
    conf = Vnets(params)
    print('Parameters used for generating:')
    print('===============================')
    pprint(conf.params_dict)
    print('\nGenerated configuration:')
    print('========================')
    pprint([item for item in conf.items()])
