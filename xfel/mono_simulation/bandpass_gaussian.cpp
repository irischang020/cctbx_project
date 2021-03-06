#include <xfel/mono_simulation/bandpass_gaussian.h>
#include <boost/math/special_functions/erf.hpp>
double
xfel::parameter::best_fit_limit( farray const& W, farray const& WS ){
  double wsum = 0.0;
  for (int i=0; i<W.size(); ++i){
    wsum += W[i];
  }
  return wsum/W.size();
}
