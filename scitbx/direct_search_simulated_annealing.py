from scitbx.array_family import flex
from libtbx.utils import Sorry
from libtbx.test_utils import approx_equal
from copy import deepcopy
from math import exp,sin
import random
from scitbx import simplex

class DSSA(object):
  """
  Directed Simplex Simulated Annealing
  http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/go_files/DSSA.pdf
  Hybrid simulated annealing and direct search method for nonlinear unconstrained global optimization
  """

  def __init__(self,
               dimension,
               matrix, # ndm * (ndm+1)
               evaluator,
               N_candidate=None,
               tolerance=1e-8,
               max_iter=1e9,
               coolfactor = 0.6,
               T_ratio = 1e4,
               simplex_scale=0.2,
               monitor_cycle=11):

    self.max_iter = max_iter
    self.dimension=dimension
    self.tolerance=tolerance
    self.evaluator = evaluator
    self.coolfactor = coolfactor
    self.T_ratio = T_ratio
    self.simplex_scale = simplex_scale
    if(N_candidate is None):
      self.N_candidate=dimension+1
    else:
      self.N_candidate=N_candidate

    if((len(matrix) != self.dimension+1) or (matrix[0].size() != self.dimension)):
       raise Sorry("The initial simplex matrix does not match dimensions specified")
    for vector in matrix[1:]:
      if (vector.size() !=  matrix[0].size()) :
        raise Sorry("Vector length in intial simplex do not match up" )

    self.monitor_cycle=monitor_cycle
    self.initialize(matrix)
    self.candidates = []
    self.optimize()
    self.optimize_further()

  def initialize(self,matrix):
    self.end=False
    self.found=False
    self.simplexValue=flex.double()
    self.matrix=[]
    for vector in matrix:
     self.matrix.append(vector.deep_copy())
     self.simplexValue.append(self.function(vector))
    self.centroid=flex.double()
    self.reflectionPt=flex.double()

  def optimize(self):
    found = False
    end = False
    self.Nstep=self.dimension
    monitor_score=0
    self.Sort()

    for point in self.matrix:
      self.candidates.append(point.deep_copy() )
    self.candi_value = self.simplexValue.deep_copy()

    rd = 0
    self.count = 0
    while ((not found ) and (not end)):
      self.explore()
      self.update_candi()

      self.count += 1
      self.min_score=self.simplexValue[0]

      if self.count%self.monitor_cycle==0:
        rd = abs(self.simplexValue[self.dimension]-self.simplexValue[0])
        rd = rd/(abs(self.min_score)+self.tolerance*self.tolerance)
        if rd < self.tolerance:
          found = True
        else:
          monitor_score = self.min_score

      if self.count>=self.max_iter or self.T < self.min_T:
        end =True

  def update_candi(self):
    for ii in range(self.dimension+1):
      for jj in range(ii, self.N_candidate):
        if self.simplexValue[ii] < self.candi_value[jj]:
          if(self.simplexValue[ii] > self.candi_value[jj-1]):
            self.candi_value.insert( jj, self.simplexValue[ii])
            self.candidates.insert( jj, self.matrix[ii].deep_copy() )
            if(self.candi_value.size() > self.N_candidate):
              self.candi_value.pop_back()
              self.candidates.pop()
          break

  def optimize_further(self):
    self.solutions=[]
    self.scores= flex.double()
    for candi in self.candidates:
      starting_simplex = []
      for ii in range(self.dimension+1):
        starting_simplex.append(flex.random_double(self.dimension)*self.simplex_scale + candi)
      optimizer = simplex.simplex_opt(     dimension=self.dimension,
                                           matrix = starting_simplex,
                                           evaluator = self.evaluator,
                                           tolerance=self.tolerance
                                     )
      self.solutions.append( optimizer.GetResult() )
      self.scores.append( optimizer.GetScore() )

    min_index = flex.min_index( self.scores )
    self.best_solution = self.solutions[ min_index ]
    self.best_score = self.scores[ min_index ]


  def explore(self):
     if(self.count == 0):
       self.T=(flex.mean(flex.pow(self.simplexValue - flex.mean(self.simplexValue), 2.0)))**0.5
       self.min_T = self.T /self.T_ratio
     elif(self.count%self.Nstep == 0):
       self.T = self.T*self.coolfactor

     for kk in range(1,self.dimension+1):
       self.FindCentroidPt(self.dimension+1-kk)
       self.FindReflectionPt(kk)
     self.Sort()

     return # end of this explore step

  def Sort(self):
    tmp_matrix=deepcopy(self.matrix)
    tmp_value=list(self.simplexValue)
    sort_value=list(self.simplexValue)
    sort_value.sort()
    indx_array=[]
    for value in sort_value:
      indx=tmp_value.index(value)
      indx_array.append(indx)
    for ii in range(self.dimension+1):
      self.matrix[ii]=tmp_matrix[indx_array[ii]]
      self.simplexValue[ii]=tmp_value[indx_array[ii]]
    return

  def FindCentroidPt(self,kk):
   self.centroid=self.matrix[0]*0
   for ii in range (kk):
     self.centroid += self.matrix[ii]
   self.centroid /= kk

  def FindReflectionPt(self,kk):
    reflect_matrix=[]
    reflect_value=[]
    self.alpha=random.random()*0.2+0.9
    for ii in range(self.dimension+1-kk, self.dimension+1):
      reflectionPt=(self.centroid*(1.0+self.alpha) - self.alpha*self.matrix[ii])
      reflect_matrix.append(reflectionPt)
      reflect_value.append(self.function(reflectionPt))
    self.reflectionPtValue=min(reflect_value)
    if(self.reflectionPtValue > self.simplexValue[0]):
      p=exp(-(self.reflectionPtValue-self.simplexValue[0])/self.T)
      #print p
      if(p >= random.random()):
        self.ReplacePt(kk, reflect_matrix, reflect_value)
    else:
      self.ReplacePt(kk, reflect_matrix, reflect_value)



  def ReplacePt(self,kk,reflect_matrix,reflect_value):
    for ii in range(self.dimension+1-kk,self.dimension+1):
      self.matrix[ii] = reflect_matrix[ii-(self.dimension+1-kk)]
      self.simplexValue[ii]=reflect_value[ii-(self.dimension+1-kk)]
    self.Sort()
    #self.update_candi()

  def GetResult(self):
    return self.best_solution

  def getCandi(self):
    return self.candidates

  def function(self,point):
    return self.evaluator.target( point )


class test_rosenbrock_function(object):
  def __init__(self, dim=4):
    self.n = dim*2
    self.dim = dim
    self.x = flex.double( self.n, 2.0 )

    self.starting_simplex=[]
    for ii in range(self.n+1):
      self.starting_simplex.append(flex.random_double(self.n) + self.x)

    self.optimizer = DSSA(dimension=self.n,
                          matrix = self.starting_simplex,
                          evaluator = self,
                          tolerance=1e-10,
                          coolfactor=0.6
                                          )
    self.x = self.optimizer.GetResult()
    for x in self.x:
      assert abs(x-1.0)<1e-2


  def target(self, vector):
    x_vec = vector[0:self.dim]
    y_vec = vector[self.dim:]
    result=0
    for x,y in zip(x_vec,y_vec):
      result+=100.0*((y-x*x)**2.0) + (1-x)**2.0
    return result




def run():
  flex.set_random_seed(0)
  test_rosenbrock_function(3)
  flex.set_random_seed(0)
  test_rosenbrock_function(4)

if __name__ == "__main__":
  run()
  print "OK"
