from __future__ import division
from cctbx import uctbx

import boost.python
ext = boost.python.import_ext("cctbx_sgtbx_ext")
from cctbx_sgtbx_ext import *

class empty: pass

from cctbx.array_family import flex
import scitbx.math
from scitbx import matrix
from boost import rational
import random
import sys

class _space_group(boost.python.injector, ext.space_group):

  def tensor_constraints(self, reciprocal_space):
    """row-reduced echelon form of coefficients
         r.transpose() * t * r - t = 0
       Mathematica code:
         r={{r0,r1,r2},{r3,r4,r5},{r6,r7,r8}}
         t={{t0,t3,t4},{t3,t1,t5},{t4,t5,t2}}
         FortranForm[Expand[Transpose[r].t.r - t]]
    """
    result = flex.int()
    for i_smx in xrange(1,self.n_smx()):
      r = self(i_smx).r()
      if (reciprocal_space):
        r = r.transpose()
      r0,r1,r2,r3,r4,r5,r6,r7,r8 = r.num()
      result.extend(flex.int((
        r0*r0-1, r3*r3,   r6*r6,   2*r0*r3, 2*r0*r6, 2*r3*r6,
        r1*r1,   r4*r4-1, r7*r7,   2*r1*r4, 2*r1*r7, 2*r4*r7,
        r2*r2,   r5*r5,   r8*r8-1, 2*r2*r5, 2*r2*r8, 2*r5*r8,
        r0*r1, r3*r4, r6*r7, r1*r3+r0*r4-1, r1*r6+r0*r7,   r4*r6+r3*r7,
        r0*r2, r3*r5, r6*r8, r2*r3+r0*r5,   r2*r6+r0*r8-1, r5*r6+r3*r8,
        r1*r2, r4*r5, r7*r8, r2*r4+r1*r5,   r2*r7+r1*r8,   r5*r7+r4*r8-1)))
    result.resize(flex.grid(result.size()//6,6))
    scitbx.math.row_echelon_form(result)
    return result

  def adp_constraints(self):
    from cctbx import adptbx
    return adptbx.constraints(space_group=self)

class space_group_info:

  __safe_for_unpickling__ = True

  def __init__(self, symbol=None, table_id=None, group=None, number=None):
    assert [symbol, group, number].count(None) >= 2
    if (number is not None):
      symbol = str(number)
    if (symbol is None):
      assert table_id is None
      self._group = group
    else:
      assert group is None
      if (table_id is None):
        self._group = space_group(space_group_symbols(symbol))
      else:
        if (isinstance(symbol, int)): symbol = str(symbol)
        self._group = space_group(space_group_symbols(symbol, table_id))
    if (self._group is not None):
      self._group.make_tidy()
    self._space_group_info_cache = empty()

  def _copy_constructor(self, other):
    self._group = other._group
    self._space_group_info_cache = other._space_group_info_cache

  def __getinitargs__(self):
    return (str(self),)

  def __getstate__(self):
    return None

  def __setstate__(self, state):
    pass

  def group(self):
    return self._group

  def type(self, tidy_cb_op=True, r_den=cb_r_den, t_den=cb_t_den):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_type")
        or cache._type_parameters != (tidy_cb_op, r_den, t_den)):
      cache._type_parameters = (tidy_cb_op, r_den, t_den)
      cache._type = space_group_type(self._group, tidy_cb_op, r_den, t_den)
    return cache._type

  def reciprocal_space_asu(self):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_reciprocal_space_asu")):
      cache._reciprocal_space_asu = reciprocal_space_asu(self.type())
    return cache._reciprocal_space_asu

  def direct_space_asu(self):
    from cctbx.sgtbx.direct_space_asu import reference_table
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_direct_space_asu")):
      reference_asu = reference_table.get_asu(self.type().number())
      cache._direct_space_asu = reference_asu.change_basis(
        self.type().cb_op().inverse())
    return cache._direct_space_asu

  def brick(self):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_brick")):
      cache._brick = brick(self.type())
    return cache._brick

  def wyckoff_table(self):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_wyckoff_table")):
      cache._wyckoff_table = wyckoff_table(self.type())
    return cache._wyckoff_table

  def structure_seminvariants(self):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_structure_seminvariants")):
      cache._structure_seminvariants = structure_seminvariants(self._group)
    return cache._structure_seminvariants

  def reference_setting(self):
    return space_group_info(symbol=self.type().number())

  def is_reference_setting(self):
    return self.type().cb_op().is_identity_op()

  def as_reference_setting(self):
    return self.change_basis(self.type().cb_op())

  def change_basis(self, cb_op):
    if (isinstance(cb_op, str)):
      cb_op = change_of_basis_op(cb_op)
    return space_group_info(group=self.group().change_basis(cb_op))

  def change_hand(self):
    return self.change_basis(self.type().change_of_hand_op())

  def primitive_setting(self):
    return self.change_basis(self.group().z2p_op())

  def __str__(self):
    cache = self._space_group_info_cache
    if (not hasattr(cache, "_lookup_symbol")):
      cache._lookup_symbol = self.type().lookup_symbol()
    return cache._lookup_symbol

  def show_summary(self, f=None, prefix="Space group: "):
    if (f is None): f = sys.stdout
    print >> f, "%s%s (No. %d)" % (
      prefix, str(self), self.type().number())

  def any_compatible_unit_cell(self, volume):
    sg_number = self.type().number()
    if   (sg_number <   3):
      params = (1., 1.3, 1.7, 83, 109, 129)
    elif (sg_number <  16):
      params = (1., 1.3, 1.7, 90, 109, 90)
    elif (sg_number <  75):
      params = (1., 1.3, 1.7, 90, 90, 90)
    elif (sg_number < 143):
      params = (1., 1., 1.7, 90, 90, 90)
    elif (sg_number < 195):
      params = (1., 1., 1.7, 90, 90, 120)
    else:
      params = (1., 1., 1., 90, 90, 90)
    unit_cell = self.type().cb_op().inverse().apply(uctbx.unit_cell(params))
    f = (volume / unit_cell.volume())**(1/3.)
    params = list(unit_cell.parameters())
    for i in xrange(3): params[i] *= f
    return uctbx.unit_cell(params)

class _tr_vec(boost.python.injector, tr_vec):

  def as_rational(self):
    return matrix.col(rational.vector(self.num(), self.den()))

class _rot_mx(boost.python.injector, rot_mx):

  def as_rational(self):
    return matrix.sqr(rational.vector(self.num(), self.den()))

class _rt_mx(boost.python.injector, rt_mx):

  def as_rational(self):
    return matrix.rt((self.r().as_rational(), self.t().as_rational()))

class _search_symmetry_flags(boost.python.injector, ext.search_symmetry_flags):

  def show_summary(self, f=None):
    if (f is None): f = sys.stdout
    print >> f, "use_space_group_symmetry:", self.use_space_group_symmetry()
    print >> f, "use_space_group_ltr:", self.use_space_group_ltr()
    print >> f, "use_normalizer_k2l:", self.use_normalizer_k2l()
    print >> f, "use_normalizer_l2n:", self.use_normalizer_l2n()
    print >> f, "use_seminvariants:", self.use_seminvariants()

class _rt_mx(boost.python.injector, ext.rt_mx):

  def __getinitargs__(self):
    return (flex.int(self.as_int_array() + (self.r().den(), self.t().den())),)

class _site_symmetry_ops(boost.python.injector, ext.site_symmetry_ops):

  def __getinitargs__(self):
    return (self.multiplicity(), self.special_op(), self.matrices())

class _site_symmetry_table(boost.python.injector, ext.site_symmetry_table):

  def __getinitargs__(self):
    return (self.indices(), self.table(), self.special_position_indices())

  def apply_symmetry_sites(self, unit_cell, sites_cart):
    sites_frac = unit_cell.fractionalization_matrix() * sites_cart
    for i_seq in self.special_position_indices():
      sites_frac[i_seq] = self.get(i_seq=i_seq).special_op() \
                        * sites_frac[i_seq]
    return unit_cell.orthogonalization_matrix() * sites_frac

  def show_special_position_shifts(self,
        special_position_settings,
        site_labels,
        sites_frac_original=None,
        sites_cart_original=None,
        sites_frac_exact=None,
        sites_cart_exact=None,
        out=None,
        prefix=""):
    assert [sites_frac_original, sites_cart_original].count(None) == 1
    assert [sites_frac_exact, sites_cart_exact].count(None) == 1
    if (out is None): out = sys.stdout
    print >> out, prefix + "Number of sites in special positions:", \
      self.special_position_indices().size()
    if (self.special_position_indices().size() > 0):
      label_len = 5
      for i_seq in self.special_position_indices():
        label_len = max(label_len, len(site_labels[i_seq]))
      label_fmt = "%%-%ds"%label_len
      print >> out, prefix \
        + "  Minimum distance between symmetrically equivalent sites: %.4g" % (
        special_position_settings.min_distance_sym_equiv())
      print >> out, prefix + "  " + label_fmt%"Label" \
        + "   Mult   Shift    Fractional coordinates"
      uc = special_position_settings.unit_cell()
      if (sites_frac_original is None):
        sites_frac_original = uc.fractionalization_matrix()*sites_cart_original
      if (sites_frac_exact is None):
        sites_frac_exact = uc.fractionalization_matrix()*sites_cart_exact
      for i_seq in self.special_position_indices():
        so = sites_frac_original[i_seq]
        se = sites_frac_exact[i_seq]
        special_ops = self.get(i_seq=i_seq)
        print >> out, prefix + "  " + label_fmt%site_labels[i_seq] \
          + "  %4d  %7.3f (%8.4f %8.4f %8.4f) original" % (
          (special_ops.multiplicity(), uc.distance(so, se)) + so)
        print >> out, prefix + label_fmt%"" \
          + "   site sym %-6s"%special_position_settings.site_symmetry(se) \
              .point_group_type() \
          + "(%8.4f %8.4f %8.4f) exact"%se
        s = str(special_ops.special_op())
        print >> out, prefix + label_fmt%"" + " "*(18+max(0,(26-len(s))//2)), s

class _wyckoff_table(boost.python.injector, wyckoff_table):

  def random_site_symmetry(self,
        special_position_settings,
        i_position,
        unit_shift_range=(-5,6),
        tolerance=1.e-8):
    position = self.position(i_position)
    run_away_counter = 0
    while 1:
      run_away_counter += 1
      assert run_away_counter < 1000
      site = position.special_op() * [random.random() for i in xrange(3)]
      if (unit_shift_range is not None):
        site = [x + random.randrange(*unit_shift_range) for x in site]
      site_symmetry = special_position_settings.site_symmetry(site)
      if (site_symmetry.distance_moved() < tolerance):
        assert site_symmetry.multiplicity() == position.multiplicity()
        return site_symmetry
