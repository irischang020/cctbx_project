#ifndef MMTBX_TLS_OPTIMISE_AMPLITUDES_H
#define MMTBX_TLS_OPTIMISE_AMPLITUDES_H

#include <string>
#include <iostream>
#include <cmath>

// Basic data types
#include <scitbx/vec3.h>
#include <scitbx/mat3.h>
#include <scitbx/sym_mat3.h>

// Allow arrays of the above
#include <scitbx/array_family/tiny.h>
#include <scitbx/array_family/versa.h>
#include <scitbx/array_family/shared.h>

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/args.hpp>
#include <boost/python/class.hpp>
#include <boost/python/module.hpp>
#include <boost/python/return_by_value.hpp>
#include <boost/python/return_value_policy.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

namespace mmtbx { namespace tls { namespace optimise {

// These are used a lot...
namespace af = scitbx::af;
namespace bp = boost::python;

// Commonly used types 
typedef scitbx::vec3<double> vec;
typedef scitbx::mat3<double> mat;
typedef scitbx::sym_mat3<double> sym;
// 1-dimensional arrays
typedef af::shared<double> dblArr1d;
typedef af::shared<size_t> selArr1d;
typedef af::shared<int>    intArr1d;
typedef af::shared<bool>   blnArr1d;
typedef af::shared<sym>    symArr1d;
// N-dimensional arrays
typedef af::versa<bool,   af::flex_grid<> > blnArrNd;
typedef af::versa<double, af::flex_grid<> > dblArrNd;
typedef af::versa<sym,    af::flex_grid<> > symArrNd;

template <typename T>
T find_max(const af::shared<T> &array)
{
  T max_val = array[0];
  for (size_t i=1; i<array.size(); i++)
  {
    if (max_val < array[i]) { max_val = array[i]; }
  }
  return max_val;
};

bool is_zero(const sym s, double tol=1e-12)
{
  if (
      (std::abs(s[0])<tol) && 
      (std::abs(s[1])<tol) && 
      (std::abs(s[2])<tol) && 
      (std::abs(s[3])<tol) && 
      (std::abs(s[4])<tol) && 
      (std::abs(s[5])<tol) 
      )
  {
    return true;
  }
  return false;
}

class MultiGroupMultiDatasetUijAmplitudeFunctionalAndGradientCalculator {

  public: 
    //! Main constructor
    MultiGroupMultiDatasetUijAmplitudeFunctionalAndGradientCalculator(
            const symArrNd &target_uijs,
            const dblArrNd &target_weights,
            const dblArr1d &base_amplitudes,
            const bp::list &base_uijs,
            const bp::list &base_atom_indices,
            const selArr1d &dataset_hash,
            const symArr1d &residual_uijs ) :
      target_uijs(target_uijs),
      target_weights(target_weights),
      dataset_hash(dataset_hash),
      residual_uijs(residual_uijs),
      n_dst(target_uijs.accessor().all()[0]),
      n_atm(target_uijs.accessor().all()[1]),
      n_base(base_amplitudes.size()),
      n_total(base_amplitudes.size() + residual_uijs.size())
    {
      std::ostringstream errMsg;
      // Check target uijs
      if (target_uijs.accessor().nd() != 2) { 
        errMsg << "invalid target_uijs: must be 2-dimensional flex array (currently " << target_uijs.accessor().nd() << ")";
        throw std::invalid_argument( errMsg.str() ); 
      }
      // Check weights
      if (target_uijs.accessor().nd() != target_weights.accessor().nd()) 
      { 
        errMsg << "invalid dimension of target_weights (dimension " << target_weights.accessor().nd() << "): must be same dimension as target_uijs (dimension " << target_uijs.accessor().nd() << ")";
        throw std::invalid_argument( errMsg.str() ); 
      }
      for (size_t i=0; i<target_uijs.accessor().nd(); i++)
      {
        if (target_uijs.accessor().all()[i] != target_weights.accessor().all()[i]) 
        {
          errMsg << "incompatible dimension of target_weights (axis " << i << "): must be same size as target_uijs (" << target_weights.accessor().all()[i] << " != " << target_uijs.accessor().all()[i] <<")";
          throw std::invalid_argument( errMsg.str() ); 
        }
      }
      // Check base_amplitudes, base_uijs and base_atom_indices (common error message)
      errMsg << "invalid input base components. "
        << "base_amplitudes (length " << base_amplitudes.size() 
        << "), base_uijs (length " << bp::len(base_uijs)
        << ") and base_atom_indices (length " << bp::len(base_atom_indices)
        << ") must all be the same length";
      if (base_amplitudes.size() != n_base) { throw std::invalid_argument( errMsg.str() ); }
      if (bp::len(base_uijs) != n_base) { throw std::invalid_argument( errMsg.str() ); }
      if (bp::len(base_atom_indices) != n_base) { throw std::invalid_argument( errMsg.str() ); }
      errMsg.str(""); // clear the previous error message
      // Unpack base_uijs and base_atom_indicess
      base_u.reserve(bp::len(base_uijs));
      base_i.reserve(bp::len(base_atom_indices));
      for (std::size_t i = 0; i < n_base; ++i) 
      {
        symArr1d* atm_u = new symArr1d(bp::extract<symArr1d>(base_uijs[i]));
        selArr1d* atm_i = new selArr1d(bp::extract<selArr1d>(base_atom_indices[i]));

        if (atm_u->size() != atm_i->size()) 
        {
          errMsg << "incompatible pair (element " << i << ") in base_uijs/base_atom_indices: pairwise elements must be the same length (" << atm_u->size() << " and " << atm_i->size() << ")";
          throw std::invalid_argument( errMsg.str() ); 
        }
        if (find_max(*atm_i) >= n_atm) 
        {
          errMsg << "invalid selection in base_atom_indices (" << find_max(*atm_i) << "): attempting to select atom outside of array (size " << n_atm << ")";
          throw std::invalid_argument( errMsg.str() ); 
        }

        base_u.push_back(atm_u);
        base_i.push_back(atm_i);
      }
      // Check dataset hash
      if (dataset_hash.size() != n_base) { 
        errMsg << "invalid dataset_hash (length " << dataset_hash.size() << "): must be same length as base_amplitudes, base_uijs & base_atom_indices (length " << base_amplitudes.size() << ")";
        throw std::invalid_argument( errMsg.str() ); 
      }
      if (find_max(dataset_hash) >= n_dst)
      { 
        errMsg << "invalid value in dataset_hash (" << find_max(dataset_hash) << "): attempts to select element outside range of target_uijs (size " << n_dst << ")";
        throw std::invalid_argument( errMsg.str() ); 
      }
      for (size_t i_dst=0; i_dst < n_dst; i_dst++)
      {
        bool found = false;
        for (size_t i_base=0; i_base < n_base; i_base++)
        {
          if (dataset_hash[i_base] == i_dst) 
          { 
            found = true; 
            break;
          }
        }
        if (found == false)
        {
          errMsg << "Dataset index " << i_dst << " is not present in dataset_hash -- this dataset has no base elements associated with it.";
          throw std::invalid_argument( errMsg.str() );
        }
      }
      // Check residual uijs
      if (residual_uijs.size() != n_atm) 
      { 
        errMsg << "invalid size of residual_uijs (" << residual_uijs.size() << "): must match 2nd dimension of target_uijs (" << n_atm << ")";
        throw std::invalid_argument( errMsg.str() ); 
      }

      // ==========================
      // Assign class members
      // ==========================

      // Initialise residual amplitude array
      dblArr1d res_amplitudes(n_atm, 1.0);

      // Concatenate amplitude arrays
      initial_amplitudes.reserve(n_total);
      std::copy(base_amplitudes.begin(), base_amplitudes.end(), std::back_inserter(initial_amplitudes));
      std::copy(res_amplitudes.begin(), res_amplitudes.end(), std::back_inserter(initial_amplitudes));
      // Copy to current values
      current_amplitudes = dblArr1d(initial_amplitudes);

      // Total Uijs (summed over levels) (datasets * atoms)
      total_uijs = symArrNd(af::flex_grid<>(n_dst, n_atm), sym(0.,0.,0.,0.,0.,0.));

      // Initialise blank residual mask
      setResidualMask(blnArr1d(n_dst, true));
    }

    dblArr1d getCurrentAmplitudes()
    {
      return current_amplitudes;
    }

    void setCurrentAmplitudes(const dblArr1d &values)
    {
      if (values.size() != current_amplitudes.size()) { 
        std::ostringstream errMsg;
        errMsg << "Input array (size " << values.size() << ") must be the same length as current_amplitudes (size " << current_amplitudes.size() << ")";
        throw std::invalid_argument( errMsg.str() );
      }
      for (size_t i=0; i<current_amplitudes.size(); i++)
      {
        current_amplitudes[i] = values[i];
      }
    }
    
    void printCurrentAmplitudes()
    {
      for (size_t i=0; i<current_amplitudes.size(); i++)
      {
        std::cout << i << " - " << current_amplitudes[i] << std::endl;
      }
    }

    void setResidualMask(const blnArr1d &mask)
    {
      if (mask.size() != n_dst) {
        std::ostringstream errMsg;
        errMsg << "Input array (size " << mask.size() << ") must be the same length as number of datasets (" << n_dst << ")";
        throw std::invalid_argument( errMsg.str() );
      }
      residual_mask = blnArr1d(mask);
      residual_mask_total = 0;
      for (size_t i=0; i<residual_mask.size(); i++)
      {
        residual_mask_total += (int)residual_mask[i];
      }
    }

    bp::tuple computeFunctionalAndGradients()
    {
      // Reset everything
      zero();
      
      n_call++;

      double functional = 0.0;
      dblArr1d gradients = dblArr1d(n_total, 0.0);
      
      // Normalisation term (number of datasets)
      double norm_all = 1. / (double)(n_dst * n_atm); 

      // Normalisation term for residual level
      double norm_res;
      if (residual_mask_total > 0)
      {
        // Upweights by term n_all/n_calc to simulate being calculated over all datasets
        norm_res = norm_all * (double)(n_dst) / (double)(residual_mask_total);
      } else {
        norm_res = 0.0; // residual level not being optimised
      }
  
      // Set negative amplitudes to zero
      for (size_t i_opt=0; i_opt<current_amplitudes.size(); i_opt++)
      {
        if (current_amplitudes[i_opt] < 0.0)
        {
          // Constrain the value to be zero (negate any benefit to the functional that could have been gained)
          current_amplitudes[i_opt] = 0.0;
        }
      }

      // Loop variables
      size_t i_opt;   // index in the list of current_amplitudes
      size_t i_dst;   // index of the appropriate dataset
      sym m;          // Use to store the amplitude-multiplied u
      sym base_sym, diff_sym;

      // ==========================================================
      // Sum over amplitudes to generate totals - !!! BASE TERMS !!!
      for (size_t i_base=0; i_base<n_base; i_base++)
      {
        symArr1d &base_u_atom = *(base_u[i_base]);
        selArr1d &base_i_atom = *(base_i[i_base]);
        i_dst = dataset_hash[i_base];
        i_opt = i_base;
          
        // Iterate through atoms associated with this base element
        for (size_t i_atm_x=0; i_atm_x<base_u_atom.size(); i_atm_x++)
        {
          // apply multipliers
          m = current_amplitudes[i_opt] * base_u_atom[i_atm_x];
          // Skip if null
          if (is_zero(m))
          { 
            continue; 
          }
          // Add to total uijs
          total_uijs(i_dst, base_i_atom[i_atm_x]) += m;
        }
      }
      // Sum over amplitudes to generate totals - !!! RESIDUAL TERMS !!!
      for (size_t i_atm=0; i_atm<n_atm; i_atm++)
      {
        i_opt = n_base + i_atm;
        m = current_amplitudes[i_opt] * residual_uijs[i_atm];
        for (size_t i_dst=0; i_dst<n_dst; i_dst++)
        {
          total_uijs(i_dst, i_atm) += m;
        }
      }
      // ==========================================================
      
      // ==========================================================
      // Calculate functional and gradients
      for (size_t i_dst=0; i_dst<n_dst; i_dst++)
      {
        // Extract weights for this dataset
        dblArr1d d_wgts(&target_weights(i_dst,0), &target_weights(i_dst, n_atm));
        // Extract total uijs for this dataset
        symArr1d d_total(&total_uijs(i_dst,0), &total_uijs(i_dst, n_atm));

        // Calculate difference to target
        symArr1d d_diffs(n_atm); // all elements will be populated
        for (size_t i_atm=0; i_atm<n_atm; i_atm++) 
        { 
          sym d_diff_i = target_uijs(i_dst,i_atm) - total_uijs(i_dst,i_atm);
          d_diffs[i_atm] = d_diff_i; 

          // Calculate functional -- least-squares component
          for (size_t i_elem=0; i_elem<6; i_elem++)
          {
            functional += (
                d_diff_i[i_elem] * 
                d_diff_i[i_elem] * 
                d_wgts[i_atm] * 
                norm_all
                );
          }
        }
  
        // Calculate gradients -- BASE TERMS 
        for (size_t i_base=0; i_base<n_base; i_base++)
        {
          // Only calculte if this base term is related to this dataset
          if (i_dst != dataset_hash[i_base])
          {
            continue;
          }

          // i_ relative to full length of amplitudes
          i_opt = i_base;

          // Extract the base elements
          symArr1d &base_u_atom = *(base_u[i_base]);
          selArr1d &base_i_atom = *(base_i[i_base]);

          // Iterate through the atoms in the base element
          for (size_t i_atm_x=0; i_atm_x<base_i_atom.size(); i_atm_x++)
          {
            // i_atm relative to n_atm
            size_t i_atm = base_i_atom[i_atm_x];

            // Extract the uij for this base element
            base_sym = base_u_atom[i_atm_x];

            // Skip this atom if the base_uij is zero at this position
            if (is_zero(base_sym)) 
            {
              continue; 
            }
            
            // Corresponding u_diff
            diff_sym = d_diffs[i_atm];

            // Gradient from least-squares
            // -2*base*diffs*wgts
            for (size_t i_elem=0; i_elem<6; i_elem++)
            {
              gradients[i_opt] += (
                  -2.0 * 
                  base_sym[i_elem] * 
                  diff_sym[i_elem] * 
                  d_wgts[i_atm] * 
                  norm_all
                  );
            }
          }
        }

        // Calculate gradients -- RESIDUAL TERMS
        if (residual_mask[i_dst]) 
        {
          for (size_t i_atm=0; i_atm<n_atm; i_atm++)
          {
            i_opt = n_base + i_atm;

            // Extract the uij for this base element
            base_sym = residual_uijs[i_atm];

            // Skip this atom if the base_uij is zero at this position
            if (is_zero(base_sym)) 
            {
              continue; 
            }

            // Corresponding u_diff
            diff_sym = d_diffs[i_atm];

            // Gradient from least-squares
            // -2*base*diffs*wgts
            for (size_t i_elem=0; i_elem<6; i_elem++)
            {
              gradients[i_opt] += (
                  -2.0 * 
                  base_sym[i_elem] * 
                  diff_sym[i_elem] * 
                  d_wgts[i_atm] * 
                  norm_res
                  );
            }
          }
        }
      }
    
      return bp::make_tuple(functional, gradients);
    }

  private:
      
    const symArrNd target_uijs;
    af::shared<symArr1d*> base_u;  // Base Uijs
    af::shared<selArr1d*> base_i;  // Atom indices for base uijs
    const symArr1d residual_uijs;
    const dblArrNd target_weights;
    
    const selArr1d dataset_hash; // maps base elements to datasets

    blnArr1d residual_mask;
    int residual_mask_total = 0;

    const size_t n_dst, n_atm, n_base, n_total;

    dblArr1d initial_amplitudes;
    dblArr1d current_amplitudes;
    
    symArrNd total_uijs;

    size_t n_call = 0;

    void zero()
    {
      // Zero-out the level uijs
      memset(&total_uijs[0], 0.0, sizeof(sym) * total_uijs.size());
    }
};

} } } // close namepsace mmtbx/tls/optimise

#endif
