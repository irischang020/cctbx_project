from __future__ import absolute_import, division, print_function
# LIBTBX_SET_DISPATCHER_NAME phenix.fest

from mmtbx.scaling import fest
import sys

if (__name__ == "__main__"):
  fest.run(args=sys.argv[1:])
