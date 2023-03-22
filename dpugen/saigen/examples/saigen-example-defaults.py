#!/usr/bin/python3
#
# Simple example demonstrating importing of dpugen and generating a
# configuration using default scaling parameters.
from pprint import pprint

from saigen.confbase import ConfBase
from saigen.confutils import common_main

import dpugen

if __name__ == '__main__':
    # Instantiate
    conf = dpugen.sai.SaiConfig()
    conf.generate()
    print('Parameters used for generating:')
    print('===============================')
    pprint(conf.params_dict)
    print('\nGenerated configuration:')
    print('========================')
    pprint(conf.items())
