#ifndef SCITBX_SPARSE_DFS_H
#define SCITBX_SPARSE_DFS_H

#include <vector>
#include <boost/tuple/tuple.hpp>
#include <stack>

namespace scitbx { namespace sparse {

/** A DFS through the graph associated to a sparse matrix, starting
from the nonzero elements of a vector.
*/
template<class Matrix>
class depth_first_search
{
public:
  typedef typename Matrix::value_type value_type;
  typedef typename Matrix::column_type column_type;
  typedef typename Matrix::row_index row_index;
  typedef typename Matrix::column_index column_index;
  typedef typename Matrix::row_iterator row_iterator;

private:
    enum colour_type {white, gray, black};
  std::vector<colour_type> colour;

  typedef typename std::vector<row_index>::iterator
    row_idx_iter;

public:
    // Construct a DFS for a matrix of at most m rows and n columns
    depth_first_search(row_index m, column_index n)
    : colour(std::max(m,n), white)
  {}

  // Perform the DFS through the graph of M, starting from the nonzeros of d
  template<class Visitor>
    void operator()(Matrix& M, column_type &d, Visitor& vis);
};

template<class Matrix>
template<class Visitor>
void depth_first_search<Matrix>::operator()(Matrix& M, column_type &d,
                                            Visitor& vis)
{
  std::vector<row_index> marked; // grayed and blackened vertices

  vis.dfs_started();

  for (row_iterator i_d=d.begin(); i_d != d.end(); i_d++) {
    /* DFS from nonzero of d */
    std::stack<boost::tuple<row_index, row_iterator, row_iterator> > stack;
    column_index l = vis.permute_rhs( i_d.index() );
    if (colour[l] != white) continue;
    vis.dfs_started_from_vertex(l);
    row_iterator col_iter = M.col(l).begin(),
                 col_end  = M.col(l).end();
    stack.push(boost::make_tuple(l, col_iter, col_end));
    while (!stack.empty()) {
      tie(l, col_iter, col_end) = stack.top();
      stack.pop();
      while (col_iter != col_end) {
        row_index k = vis.permute( col_iter.index() );
        if (colour[k] == white) {
          colour[k] = gray; marked.push_back(k);
          vis.dfs_found_tree_edge(l, k);
          if (vis.dfs_shall_cut_tree_edge(l, k)) continue;
          stack.push(boost::make_tuple(l, ++col_iter, col_end));
          l = k;
          col_iter = M.col(l).begin();
          col_end  = M.col(l).end();
        }
        else {
          ++col_iter;
        }
      }
      colour[l] = black; marked.push_back(l);
      vis.dfs_finished_vertex(l);
    }
  }
  /* Reset colour array for the next depth-first search.
    That's an important trick to keep the total number of ops
    proportional to the number of non-zeroes: if we were to reset
    the entire vector colour, we would run in O(n)
  */
  for (row_idx_iter p = marked.begin(); p != marked.end(); p++) {
    colour[*p] = white;
  }
}

}} // scitbx::sparse

#endif
