#!/usr/bin/python3
#
# Simple example demonstrating importing of dpugen and generating a
# configuration using default scaling parameters.
import dpugen
from saigen.confbase import *
from saigen.confutils import *
from pprint import pprint

if __name__ == '__main__':
    # Instantiate
    conf = dpugen.sai.SaiConfig()
    conf.generate()
    pprint(conf.items())