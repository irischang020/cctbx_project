/* Copyright (c) 2001-2002 The Regents of the University of California
   through E.O. Lawrence Berkeley National Laboratory, subject to
   approval by the U.S. Department of Energy.
   See files COPYRIGHT.txt and LICENSE.txt for further details.

   Revision history:
     2003 Mar: Created (rwgk)
 */

#include <scitbx/array_family/boost_python/flex_fwd.h>

#include <scitbx/histogram.h>
#include <boost/python/class.hpp>
#include <boost/python/overloads.hpp>

namespace scitbx { namespace af { namespace boost_python { namespace {

  struct histogram_wrappers
  {
    typedef histogram<> w_t;

    BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(
      get_cutoff_overloads, get_cutoff, 1, 2)

    static void
    wrap()
    {
      using namespace boost::python;
      class_<w_t>("histogram", no_init)
        .def(init<af::const_ref<double> const&,
                  optional<std::size_t> >())
        .def("data_min", &w_t::data_min)
        .def("data_max", &w_t::data_max)
        .def("slot_width", &w_t::slot_width)
        .def("slots", &w_t::slots)
        .def("get_cutoff", &w_t::get_cutoff, get_cutoff_overloads())
      ;
    }
  };

} // namespace <anonymous>

  void wrap_flex_histogram()
  {
    histogram_wrappers::wrap();
  }

}}} // namespace scitbx::af::boost_python
