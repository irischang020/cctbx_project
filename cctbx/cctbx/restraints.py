import cctbx.crystal.direct_space_asu
import cctbx.array_family.flex
import scitbx.array_family.shared

import boost.python
ext = boost.python.import_ext("cctbx_restraints_ext")
from cctbx_restraints_ext import *

import scitbx.stl.map

repulsion_radius_table = scitbx.stl.map.stl_string_double

repulsion_distance_table = scitbx.stl.map.stl_string_stl_map_stl_string_double
repulsion_distance_dict = scitbx.stl.map.stl_string_double
