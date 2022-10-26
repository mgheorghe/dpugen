from __future__ import unicode_literals
from __future__ import absolute_import

import logging

# Logging configuration
log = logging.getLogger(__name__)  # noqa
log.addHandler(logging.NullHandler())  # noqa

import sys
import os

sys.path.append(os.path.dirname(__file__))
__version__ = "0.0.5"
PY_MAJ_VER = 3
PY_MIN_VER = 5
MIN_PYTHON_VER = "3.5"


# Make sure user is using a valid Python version (for DpuGen)
def check_python_version():  # type: ignore
    python_snake = "\U0001F40D"

    # Use old-school .format() method in case someone tries to use DpuGen with very old Python
    msg = """DpuGen Version {net_ver} requires Python Version {py_ver} or higher.""".format(net_ver=__version__, py_ver=MIN_PYTHON_VER)
    if sys.version_info.major != PY_MAJ_VER:
        raise ValueError(msg)
    elif sys.version_info.minor < PY_MIN_VER:
        # Why not :-)
        msg = msg.rstrip() + " {snake}\n\n".format(snake=python_snake)
        raise ValueError(msg)


check_python_version()  # type: ignore




from .sai import *
#from .dash import *



