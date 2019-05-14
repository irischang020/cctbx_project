from __future__ import absolute_import, division, print_function
# LIBTBX_SET_DISPATCHER_NAME phenix.cablam_idealization

from iotbx.cli_parser import run_program
from mmtbx.programs import cablam_idealization

run_program(cablam_idealization.Program)
