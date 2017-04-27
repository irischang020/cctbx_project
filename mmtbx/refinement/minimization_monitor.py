from __future__ import division
from libtbx import adopt_init_args, Auto

class minimization_monitor(object):
  def __init__(self,
      number_of_cycles,
      max_number_of_cycles,
      mode="simple_cycles"):
    adopt_init_args(self, locals())
    assert self.mode in ["simple_cycles", "min_outliers", "no_outliers"]
    self.current_cycle = 0
    self.cycles_params = []
    self.cycles_geometry = [] # mmtbx.model_statistics.geometry_no_grm

  def need_more_cycles(self):
    if self.current_cycle == 0:
      return True
    if self.current_cycle >= self.max_number_of_cycles:
      return False
    if self.number_of_cycles is not Auto:
      return self.current_cycle < self.number_of_cycles
    elif self.mode == "min_outliers":
      return self.geometry_improved() or not self.geometry_is_ok()
    elif self.mode == "no_outliers":
      return not (self.geometry_is_perfect() or self.no_5_cycles_improvement())

  def save_cycle_results(self, geometry=None):
    self.current_cycle += 1
    if geometry is None:
      assert self.mode == "simple_cycles", "Need geometry validation for decision making in other running modes"
    else:
      self.cycles_geometry.append(geometry)

  def geometry_improved(self):
    if len(self.cycles_geometry) > 1:
      for geometry_param in ["ramachandran_outliers", "n_twisted_general"]:
        if getattr(self.cycles_geometry[-2], geometry_param) > getattr(self.cycles_geometry[-1], geometry_param):
          return True
    else:
      return False

  def get_current_cycle_n(self):
    return self.current_cycle

  def same_geometry(self, g1, g2):
    for geometry_param in ["ramachandran_outliers", "n_twisted_general"]:
      if abs(getattr(g1, geometry_param) - getattr(g2, geometry_param)) > 0.01:
        return False
    return True

  def no_5_cycles_improvement(self):
    if len(self.cycles_geometry) < 5:
      return False
    for i in range(1,5):
      if not self.same_geometry(self.cycles_geometry[-i], self.cycles_geometry[-i-1]):
        return False
    return True

  def geometry_is_perfect(self):
    if len(self.cycles_geometry) == 0:
      return False
    else:
      if (self.cycles_geometry[-1].ramachandran_outliers < 0.01 and
          self.cycles_geometry[-1].twisted_general + self.cycles_geometry[-1].twisted_proline < 0.01):
        return True
    return False

  def geometry_is_ok(self):
    if len(self.cycles_geometry) == 0:
      return False
    else:
      if (self.cycles_geometry[-1].ramachandran_outliers < 2 or
          self.cycles_geometry[-1].twisted_general + self.cycles_geometry[-1].twisted_proline < 2):
        return True
    return False

  def need_weight_optimization(self):
    # currently once in 3 macro-cycles
    return True
    result = False
    if self.current_cycle == 0:
      result = True
    elif len(self.cycles_params) < 3:
      result = False
    else:
      result = True
      for i in xrange(1,4):
        if self.cycles_params[-i]["did_wo"]:
          result = False
    self.cycles_params.append({"did_wo": result})
    return result