from __future__ import division
from scitbx import matrix
from mmtbx.tls import tls_as_xyz
from libtbx import group_args
from libtbx.test_utils import approx_equal

def print_step(m):
  print "-"*80
  tls_as_xyz.print_step(m)

def extract(s):
  def fetch_matrix_1_sym(x,y,z):
    return matrix.sym(sym_mat3=[x[0], y[1], z[2], x[1], x[2], y[2]])
  def fetch_matrix_2_sym(x,y,z):
    return matrix.sym(sym_mat3=[x[3], y[4], z[5], x[4], x[5], y[5]])
  def fetch_matrix_3_sym(x,y,z):
    return matrix.sym(sym_mat3=[x[6], y[7], z[8], x[7], x[8], y[8]])
  def fetch_matrix_3_sqr(x,y,z):
    return matrix.sqr([x[6], x[7], x[8], y[6], y[7], y[8], z[6], z[7], z[8]])
  def get_next_3_lines(i, lines):
    x = lines[i+1].split()
    y = lines[i+2].split()
    z = lines[i+3].split()
    return x,y,z
  def get_next_3_lines_all_float(i, lines):
    x = [float(j) for j in lines[i+1].split()]
    y = [float(j) for j in lines[i+2].split()]
    z = [float(j) for j in lines[i+3].split()]
    return x,y,z
  read            = False
  read_T_L_S      = False
  read_lx_ly_lz   = False
  read_TL_LL_SL   = False
  read_wL         = False
  read_CLW_CLS_CL = False
  read_VL         = False
  read_VM         = False
  read_vx_vy_vz   = False
  read_VV         = False
  lines = s.splitlines()
  for i, l in enumerate(lines):
    if(l.count("************* INFORMATION FOR COMPARISON **********")):
      read=True
    if(read):
      ### set conditions
      #
      if(l.startswith("***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***")):
        read_T_L_S = True
      #
      if(l.startswith("***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)")):
        read_lx_ly_lz = True
      #
      if(l.startswith("***  T[L] L[L] S[L] *** total TLS matrices in the L base ***")):
        read_TL_LL_SL = True
      #
      if(l.startswith("***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base")):
        read_wL = True
      #
      if(l.startswith("***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***")):
        read_CLW_CLS_CL = True
      #
      if(l.startswith("***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base")):
        read_VL = True
      #
      if(l.startswith("***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base")):
        read_VM = True
      #
      if(l.startswith("***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)")):
        read_vx_vy_vz = True
      #
      if(l.startswith("***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base")):
        read_VV = True
      #
      ### extract
      #
      if(read_T_L_S):
        read_T_L_S = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        T_M = fetch_matrix_1_sym(x,y,z)
        L_M = fetch_matrix_2_sym(x,y,z)
        S_M = fetch_matrix_3_sqr(x,y,z)
      #
      if(read_lx_ly_lz):
        read_lx_ly_lz = False
        x,y,z = get_next_3_lines(i, lines)
        l_x = matrix.col((float(x[1]), float(x[2]), float(x[3])))
        l_y = matrix.col((float(y[1]), float(y[2]), float(y[3])))
        l_z = matrix.col((float(z[1]), float(z[2]), float(z[3])))
      #
      if(read_TL_LL_SL):
        read_TL_LL_SL = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        T_L = fetch_matrix_1_sym(x,y,z)
        L_L = fetch_matrix_2_sym(x,y,z)
        S_L = fetch_matrix_3_sqr(x,y,z)
      #
      if(read_wL):
        read_wL = False
        x,y,z = get_next_3_lines(i, lines)
        w_lx = matrix.col((float(x[7]), float(x[8]), float(x[9])))
        w_ly = matrix.col((float(y[7]), float(y[8]), float(y[9])))
        w_lz = matrix.col((float(z[7]), float(z[8]), float(z[9])))
      #
      if(read_CLW_CLS_CL):
        read_CLW_CLS_CL = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        C_LW = fetch_matrix_1_sym(x,y,z)
        C_LS = fetch_matrix_2_sym(x,y,z)
        C_L  = fetch_matrix_3_sym(x,y,z)
      #
      if(read_VL):
        read_VL = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        V_L = fetch_matrix_1_sym(x,y,z)
      #
      if(read_VM):
        read_VM = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        V_M = fetch_matrix_1_sym(x,y,z)
      #
      if(read_vx_vy_vz):
        read_vx_vy_vz = False
        x,y,z = get_next_3_lines(i, lines)
        v_x = matrix.col((float(x[1]), float(x[2]), float(x[3])))
        v_y = matrix.col((float(y[1]), float(y[2]), float(y[3])))
        v_z = matrix.col((float(z[1]), float(z[2]), float(z[3])))
      #
      if(read_VV):
        read_VV = False
        x,y,z = get_next_3_lines_all_float(i, lines)
        V_V = fetch_matrix_1_sym(x,y,z)
      #
  return group_args(
    T_M=T_M,
    L_M=L_M,
    S_M=S_M,
    l_x=l_x,
    l_y=l_y,
    l_z=l_z,
    T_L=T_L,
    L_L=L_L,
    S_L=S_L,
    w_lx=w_lx,
    w_ly=w_ly,
    w_lz=w_lz,
    C_LW=C_LW,
    C_LS=C_LS,
    C_L =C_L ,
    V_L=V_L,
    V_M=V_M,
    v_x=v_x,
    v_y=v_y,
    v_z=v_z,
    V_V=V_V)

def compare(e, r, eps = 1.e-5):
  # e - extract object, r - result object
  assert approx_equal(e.T_M , r.T       , eps)
  assert approx_equal(e.L_M , r.L       , eps)
  assert approx_equal(e.S_M , r.S       , eps)
  assert approx_equal(e.l_x , r.b_o.l_x , eps)
  assert approx_equal(e.l_y , r.b_o.l_y , eps)
  assert approx_equal(e.l_z , r.b_o.l_z , eps)
  assert approx_equal(e.T_L , r.b_o.T_L , eps)
  assert approx_equal(e.L_L , r.b_o.L_L , eps)
  assert approx_equal(e.S_L , r.b_o.S_L , eps)
  assert approx_equal(e.w_lx, r.c_o.w_lx, eps)
  assert approx_equal(e.w_ly, r.c_o.w_ly, eps)
  assert approx_equal(e.w_lz, r.c_o.w_lz, eps)
  assert approx_equal(e.C_LW, r.C_LW    , eps)
  assert approx_equal(e.C_LS, r.g_o.C_LS, eps)
  assert approx_equal(e.C_L , r.g_o.C_L , eps)
  assert approx_equal(e.V_L , r.g_o.V_L , eps)
  assert approx_equal(e.V_M , r.h_o.V_M , eps)
  assert approx_equal(e.v_x , r.h_o.v_x , eps)
  assert approx_equal(e.v_y , r.h_o.v_y , eps)
  assert approx_equal(e.v_z , r.h_o.v_z , eps)
  assert approx_equal(e.V_V , r.h_o.V_V , eps)


getTLS3_test001 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   0.00000   0.00000
   0.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   0.00000   0.00000
   0.00000   1.00000   0.00000

principal Libration axes (orthonormal L base)
L1=   1.00000   0.00000   0.00000
L2=   0.00000   1.00000   0.00000
L3=   0.00000   0.00000   1.00000

principal Vibration axes (orthonormal V base)
V1=   1.00000   0.00000   0.00000
V2=   0.00000   1.00000   0.00000
V3=   0.00000   0.00000   1.00000

TLS matrices from Libration in the L-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000
TLS matrices from Libration in the M-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.01000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   1.00000   0.00000   0.00000
Ly=   0.00000   1.00000   0.00000
Lz=   0.00000   0.00000   1.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.01000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  dx  dy  dz      *** rms : Libration around lx,ly,lz
 0.1000000 0.2000000 0.3000000

***  dx2 dy2 dz2     *** rms2: Libration around lx,ly,lz
 0.0100000 0.0400000 0.0900000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base
  0.01000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.64000005

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base
  0.01000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.64000005

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   1.00000   0.00000   0.00000
Vy=   0.00000   1.00000   0.00000
Vz=   0.00000   0.00000   1.00000

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base
  0.01000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.64000005
"""

getTLS3_test004 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   0.00000   0.00000
   0.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   2.00000   3.00000
   3.00000   1.00000   0.00000

principal Libration axes (orthonormal L base)
L1=   1.00000   0.00000   0.00000
L2=   0.00000   1.00000   0.00000
L3=   0.00000   0.00000   1.00000

principal Vibration axes (orthonormal V base)
V1=   0.26726   0.53452   0.80178
V2=   0.92212   0.09969  -0.37383
V3=  -0.27975   0.83925  -0.46625

TLS matrices from Libration in the L-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000
TLS matrices from Libration in the M-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.18685097 -0.13412423  0.03046584
 -0.13412423  0.45522982 -0.25211182
  0.03046584 -0.25211182  0.16791928


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.18685097 -0.13412423  0.03046584    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
 -0.13412423  0.45522982 -0.25211182    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.03046584 -0.25211182  0.16791928    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   1.00000   0.00000   0.00000
Ly=   0.00000   1.00000   0.00000
Lz=   0.00000   0.00000   1.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.18685097 -0.13412423  0.03046584    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
 -0.13412423  0.45522982 -0.25211182    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.03046584 -0.25211182  0.16791928    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base
  0.18685097 -0.13412423  0.03046584    0.18685097 -0.13412423  0.03046584
 -0.13412423  0.45522982 -0.25211182   -0.13412423  0.45522982 -0.25211182
  0.03046584 -0.25211182  0.16791928    0.03046584 -0.25211182  0.16791928

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base
  0.18685097 -0.13412423  0.03046584    0.18685097 -0.13412423  0.03046584
 -0.13412423  0.45522982 -0.25211182   -0.13412423  0.45522982 -0.25211182
  0.03046584 -0.25211182  0.16791928    0.03046584 -0.25211182  0.16791928

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.26726   0.53452   0.80178
Vy=   0.92212   0.09969  -0.37383
Vz=  -0.27975   0.83925  -0.46625

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base
  0.01000000  0.00000000  0.00000000    0.00999999  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000004 -0.00000001
  0.00000000  0.00000000  0.64000005   -0.00000001  0.00000000  0.64000005
"""

getTLS3_test011 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

principal Libration axes (orthonormal L base)
L1=   0.70711   0.70711   0.00000
L2=   0.00000   0.00000   1.00000
L3=   0.70711  -0.70711   0.00000

principal Vibration axes (orthonormal V base)
V1=   0.70711   0.70711   0.00000
V2=   0.00000   0.00000   1.00000
V3=   0.70711  -0.70711   0.00000

TLS matrices from Libration in the L-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000
TLS matrices from Libration in the M-base
  0.00000000  0.00000000  0.00000000    0.05000000 -0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000   -0.04000000  0.05000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.04000000    0.00000000  0.00000000  0.00000000

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.32500002 -0.31500000  0.00000000
 -0.31500000  0.32500002  0.00000000
  0.00000000  0.00000000  0.16000001


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.32500002 -0.31500000  0.00000000    0.05000000 -0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
 -0.31500000  0.32500002  0.00000000   -0.04000000  0.05000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.16000001    0.00000000  0.00000000  0.04000000    0.00000000  0.00000000  0.00000000

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.70711   0.70711   0.00000
Ly=   0.00000   0.00000   1.00000
Lz=   0.70711  -0.70711   0.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.01000003  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000001  0.00000000  0.63999999    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base
  0.01000003  0.00000000  0.00000000    0.01000003  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000001  0.00000000  0.63999999    0.00000001  0.00000000  0.63999999

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base
  0.32500002 -0.31500000  0.00000000    0.32499999 -0.31499997  0.00000000
 -0.31500000  0.32500002  0.00000000   -0.31499997  0.32499999  0.00000000
  0.00000000  0.00000000  0.16000001    0.00000000  0.00000000  0.16000001

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.70711   0.70711   0.00000
Vy=   0.00000   0.00000   1.00000
Vz=   0.70711  -0.70711   0.00000

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base
  0.01000000  0.00000000  0.00000000    0.01000002  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000000  0.63999993
"""

getTLS3_test014 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   2.00000   3.00000
   3.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   1.00000
   1.00000   0.00000   0.00000

principal Libration axes (orthonormal L base)
L1=   0.26726   0.53452   0.80178
L2=   0.92212   0.09969  -0.37383
L3=  -0.27975   0.83925  -0.46625

principal Vibration axes (orthonormal V base)
V1=   0.57735   0.57735   0.57735
V2=   0.81650  -0.40825  -0.40825
V3=   0.00000   0.70711  -0.70711

TLS matrices from Libration in the L-base
  0.00000000  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000
TLS matrices from Libration in the M-base
  0.00000000  0.00000000  0.00000000    0.04177019 -0.01602484  0.00009317    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000   -0.01602484  0.06664596 -0.03242236    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00009317 -0.03242236  0.03158385    0.00000000  0.00000000  0.00000000

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.11000001 -0.05000000 -0.05000000
 -0.05000000  0.34999996 -0.28999996
 -0.05000000 -0.28999996  0.34999996


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.11000001 -0.05000000 -0.05000000    0.04177019 -0.01602484  0.00009317    0.00000000  0.00000000  0.00000000
 -0.05000000  0.34999996 -0.28999996   -0.01602484  0.06664596 -0.03242236    0.00000000  0.00000000  0.00000000
 -0.05000000 -0.28999996  0.34999996    0.00009317 -0.03242236  0.03158385    0.00000000  0.00000000  0.00000000

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.26726   0.53452   0.80178
Ly=   0.92212   0.09969  -0.37383
Lz=  -0.27975   0.83925  -0.46625

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.04857142 -0.08232684 -0.09121538    0.01000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
 -0.08232684  0.19281989  0.14534362    0.00000000  0.04000000  0.00000000    0.00000000  0.00000000  0.00000000
 -0.09121536  0.14534362  0.56860864    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.00000000

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.00000000

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base
  0.04857142 -0.08232684 -0.09121538    0.04857142 -0.08232684 -0.09121538
 -0.08232684  0.19281989  0.14534362   -0.08232684  0.19281989  0.14534362
 -0.09121536  0.14534362  0.56860864   -0.09121536  0.14534362  0.56860864

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base
  0.11000001 -0.05000000 -0.05000000    0.11000003 -0.04999999 -0.05000001
 -0.05000000  0.34999996 -0.28999996   -0.04999999  0.34999999 -0.28999996
 -0.05000000 -0.28999996  0.34999996   -0.05000002 -0.28999996  0.34999996

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.57735   0.57735   0.57735
Vy=   0.81650  -0.40825  -0.40825
Vz=   0.00000   0.70711  -0.70711

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base
  0.01000000  0.00000000  0.00000000    0.01000001  0.00000001  0.00000002
  0.00000000  0.16000001  0.00000000    0.00000001  0.16000003  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000003  0.00000001  0.63999981
"""

getTLS3_test021 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 parallel to j : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 parallel to k : (wkx,wky,wkz)=    4.00000   1.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

principal Libration axes (orthonormal L base)
L1=   0.70711   0.70711   0.00000
L2=   0.00000   0.00000   1.00000
L3=   0.70711  -0.70711   0.00000

principal Vibration axes (orthonormal V base)
V1=   0.70711   0.70711   0.00000
V2=   0.00000   0.00000   1.00000
V3=   0.70711  -0.70711   0.00000

TLS matrices from Libration in the L-base
  0.25000000 -0.36000001  0.08000001    0.01000000  0.00000000  0.00000000    0.00000000  0.03000000 -0.02000000
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.04000000  0.00000000   -0.08000001  0.00000000 -0.04000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.00000000
TLS matrices from Libration in the M-base
  0.24499999  0.08499999 -0.29698485    0.05000000 -0.04000000  0.00000000    0.03500000  0.05500000 -0.23334524
  0.08499999  0.08499999 -0.21213204   -0.04000000  0.05000000  0.00000000   -0.05500000 -0.03500000  0.27577165
 -0.29698485 -0.21213204  1.53000009    0.00000000  0.00000000  0.04000000   -0.08485281 -0.02828427  0.00000000

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.32500002 -0.31500000  0.00000000
 -0.31500000  0.32500002  0.00000000
  0.00000000  0.00000000  0.16000001


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.56999999 -0.23000000 -0.29698485    0.05000000 -0.04000000  0.00000000    0.03500000  0.05500000 -0.23334524
 -0.23000000  0.41000003 -0.21213204   -0.04000000  0.05000000  0.00000000   -0.05500000 -0.03500000  0.27577165
 -0.29698485 -0.21213204  1.69000006    0.00000000  0.00000000  0.04000000   -0.08485281 -0.02828427  0.00000000

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.70711   0.70711   0.00000
Ly=   0.00000   0.00000   1.00000
Lz=   0.70711  -0.70711   0.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.25999996 -0.35999998  0.07999998    0.01000000  0.00000000  0.00000000    0.00000000  0.03000000 -0.02000000
 -0.35999998  1.69000006 -0.05999999    0.00000000  0.04000000  0.00000000   -0.08000001  0.00000000 -0.04000000
  0.07999997 -0.05999999  0.71999997    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.00000000

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    4.00000   1.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    2.12132  -2.12132   2.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.70711  -2.12132   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    2.82843   2.82843   1.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.25000000 -0.36000001  0.08000001    0.00000000  0.00000000  0.00000000    0.25000000 -0.36000001  0.08000001
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.00000000  0.00000000   -0.36000001  1.53000009 -0.06000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.00000000    0.08000001 -0.06000000  0.08000001

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base
  0.01000003  0.00000000  0.00000000    0.00999996  0.00000003 -0.00000003
  0.00000000  0.16000001  0.00000000    0.00000003  0.15999997  0.00000001
  0.00000001  0.00000000  0.63999999   -0.00000004  0.00000001  0.63999999

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base
  0.32500002 -0.31500000  0.00000000    0.32499993 -0.31500000  0.00000003
 -0.31500000  0.32500002  0.00000000   -0.31500000  0.32500002  0.00000002
  0.00000000  0.00000000  0.16000001    0.00000003  0.00000002  0.15999997

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.70711   0.70711   0.00000
Vy=   0.00000   0.00000   1.00000
Vz=   0.70711  -0.70711   0.00000

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base
  0.01000000  0.00000000  0.00000000    0.00999999  0.00000003 -0.00000004
  0.00000000  0.16000001  0.00000000    0.00000003  0.15999997  0.00000001
  0.00000000  0.00000000  0.64000005   -0.00000002  0.00000001  0.63999993
"""

getTLS3_test024 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   2.00000   3.00000
   3.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 parallel to j : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 parallel to k : (wkx,wky,wkz)=    4.00000   1.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   1.00000
   1.00000   0.00000   0.00000

principal Libration axes (orthonormal L base)
L1=   0.26726   0.53452   0.80178
L2=   0.92212   0.09969  -0.37383
L3=  -0.27975   0.83925  -0.46625

principal Vibration axes (orthonormal V base)
V1=   0.57735   0.57735   0.57735
V2=   0.81650  -0.40825  -0.40825
V3=   0.00000   0.70711  -0.70711

TLS matrices from Libration in the L-base
  0.25000000 -0.36000001  0.08000001    0.01000000  0.00000000  0.00000000    0.00000000  0.03000000 -0.02000000
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.04000000  0.00000000   -0.08000001  0.00000000 -0.04000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.00000000
TLS matrices from Libration in the M-base
  1.16664422 -0.06823526 -0.70200294    0.04177019 -0.01602484  0.00009317    0.08563004 -0.07749246 -0.10029086
 -0.06823528  0.16635178  0.11748905   -0.01602484  0.06664596 -0.03242236   -0.24165380 -0.00472804  0.16796263
 -0.70200288  0.11748905  0.52700424    0.00009317 -0.03242236  0.03158385    0.17404011  0.01177818 -0.08090200

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.11000001 -0.05000000 -0.05000000
 -0.05000000  0.34999996 -0.28999996
 -0.05000000 -0.28999996  0.34999996


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  1.27664423 -0.11823526 -0.75200295    0.04177019 -0.01602484  0.00009317    0.08563004 -0.07749246 -0.10029086
 -0.11823528  0.51635176 -0.17251091   -0.01602484  0.06664596 -0.03242236   -0.24165380 -0.00472804  0.16796263
 -0.75200289 -0.17251092  0.87700421    0.00009317 -0.03242236  0.03158385    0.17404011  0.01177818 -0.08090200

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.26726   0.53452   0.80178
Ly=   0.92212   0.09969  -0.37383
Lz=  -0.27975   0.83925  -0.46625

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.29857135 -0.44232675 -0.01121536    0.01000000  0.00000000  0.00000000    0.00000000  0.03000000 -0.02000000
 -0.44232675  1.72282040  0.08534358    0.00000000  0.04000000  0.00000000   -0.08000001  0.00000000 -0.04000000
 -0.01121536  0.08534360  0.64860868    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.00000000

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    4.00000   1.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    1.00499   2.71714  -2.14642
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -0.82676   1.14399  -1.73429
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    1.99117   2.23778   2.83330

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
  0.000000  0.000000  0.000000

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.25000000 -0.36000001  0.08000001    0.00000000  0.00000000  0.00000000    0.25000000 -0.36000001  0.08000001
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.00000000  0.00000000   -0.36000001  1.53000009 -0.06000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.00000000    0.08000001 -0.06000000  0.08000001

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base 
  0.04857142 -0.08232684 -0.09121538    0.04857135 -0.08232674 -0.09121536
 -0.08232684  0.19281989  0.14534362   -0.08232674  0.19282031  0.14534359
 -0.09121536  0.14534362  0.56860864   -0.09121536  0.14534360  0.56860870

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base 
  0.11000001 -0.05000000 -0.05000000    0.11000045 -0.04999994 -0.05000009
 -0.05000000  0.34999996 -0.28999996   -0.04999993  0.34999999 -0.29000005
 -0.05000000 -0.28999996  0.34999996   -0.05000011 -0.29000002  0.34999990

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.57735   0.57735   0.57735
Vy=   0.81650  -0.40825  -0.40825
Vz=   0.00000   0.70711  -0.70711

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base 
  0.01000000  0.00000000  0.00000000    0.01000007  0.00000024  0.00000011
  0.00000000  0.16000001  0.00000000    0.00000024  0.16000026  0.00000005
  0.00000000  0.00000000  0.64000005    0.00000010  0.00000008  0.63999987
"""

getTLS3_test031 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.500000 -0.300000  0.700000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

modified shifts sx,sy,sz for the libration axes and the trace
 -1.366667 -0.766667  0.492593            0.056000  0.000000

principal Libration axes (orthonormal L base)
L1=   0.70711   0.70711   0.00000
L2=   0.00000   0.00000   1.00000
L3=   0.70711  -0.70711   0.00000

principal Vibration axes (orthonormal V base)
V1=   0.70711   0.70711   0.00000
V2=   0.00000   0.00000   1.00000
V3=   0.70711  -0.70711   0.00000

TLS matrices from Libration in the L-base
  0.01867778  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000   -0.01366667  0.00000000  0.00000000
  0.00000000  0.02351111  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000 -0.03066667  0.00000000
  0.00000000  0.00000000  0.02183827    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.04433334
TLS matrices from Libration in the M-base
  0.02025802 -0.00158024  0.00000000    0.05000000 -0.04000000  0.00000000    0.01533333 -0.02900000  0.00000000
 -0.00158024  0.02025802  0.00000000   -0.04000000  0.05000000  0.00000000   -0.02900000  0.01533333  0.00000000
  0.00000000  0.00000000  0.02351111    0.00000000  0.00000000  0.04000000    0.00000000  0.00000000 -0.03066667

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.32500002 -0.31500000  0.00000000
 -0.31500000  0.32500002  0.00000000
  0.00000000  0.00000000  0.16000001


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.34525806 -0.31658024  0.00000000    0.05000000 -0.04000000  0.00000000    0.01533333 -0.02900000  0.00000000
 -0.31658024  0.34525806  0.00000000   -0.04000000  0.05000000  0.00000000   -0.02900000  0.01533333  0.00000000
  0.00000000  0.00000000  0.18351112    0.00000000  0.00000000  0.04000000    0.00000000  0.00000000 -0.03066667

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.70711   0.70711   0.00000
Ly=   0.00000   0.00000   1.00000
Lz=   0.70711  -0.70711   0.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.02867781  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000   -0.01366667  0.00000000  0.00000000
  0.00000000  0.18351112  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000 -0.03066667  0.00000000
  0.00000001  0.00000000  0.66183829    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.04433334

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
 -1.366667 -0.766667  0.492593

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.01867778  0.00000000  0.00000000    0.01867778  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.02351111  0.00000000    0.00000000  0.02351111  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.02183827    0.00000000  0.00000000  0.02183827

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base 
  0.01000003  0.00000000  0.00000000    0.01000003  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000001  0.00000000  0.63999999    0.00000001  0.00000000  0.64000005

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base 
  0.32500002 -0.31500000  0.00000000    0.32500002 -0.31500000  0.00000000
 -0.31500000  0.32500002  0.00000000   -0.31500000  0.32500002  0.00000000
  0.00000000  0.00000000  0.16000001    0.00000000  0.00000000  0.16000001

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.70711   0.70711   0.00000
Vy=   0.00000   0.00000   1.00000
Vz=   0.70711  -0.70711   0.00000

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base 
  0.01000000  0.00000000  0.00000000    0.01000003  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000001  0.00000000  0.63999999
"""

getTLS3_test034 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   2.00000   3.00000
   3.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 parallel to j : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 parallel to k : (wkx,wky,wkz)=    0.00000   0.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.500000 -0.300000  0.700000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   1.00000
   1.00000   0.00000   0.00000

modified shifts sx,sy,sz for the libration axes and the trace
 -1.366667 -0.766667  0.492593            0.056000  0.000000

principal Libration axes (orthonormal L base)
L1=   0.26726   0.53452   0.80178
L2=   0.92212   0.09969  -0.37383
L3=  -0.27975   0.83925  -0.46625

principal Vibration axes (orthonormal V base)
V1=   0.57735   0.57735   0.57735
V2=   0.81650  -0.40825  -0.40825
V3=   0.00000   0.70711  -0.70711

TLS matrices from Libration in the L-base
  0.01867778  0.00000000  0.00000000    0.01000000  0.00000000  0.00000000   -0.01366667  0.00000000  0.00000000
  0.00000000  0.02351111  0.00000000    0.00000000  0.04000000  0.00000000    0.00000000 -0.03066667  0.00000000
  0.00000000  0.00000000  0.02183827    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.04433334
TLS matrices from Libration in the M-base
  0.02303496 -0.00029772 -0.00125391    0.04177019 -0.01602484  0.00009317   -0.02358282 -0.01518012  0.01342547
 -0.00029772  0.02095190 -0.00141684   -0.01602484  0.06664596 -0.03242236   -0.01518013  0.02701657 -0.02206211
 -0.00125391 -0.00141684  0.02004031    0.00009317 -0.03242236  0.03158385    0.01342547 -0.02206211 -0.00343375

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.11000001 -0.05000000 -0.05000000
 -0.05000000  0.34999996 -0.28999996
 -0.05000000 -0.28999996  0.34999996


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.13303497 -0.05029772 -0.05125391    0.04177019 -0.01602484  0.00009317   -0.02358282 -0.01518012  0.01342547
 -0.05029772  0.37095186 -0.29141679   -0.01602484  0.06664596 -0.03242236   -0.01518013  0.02701657 -0.02206211
 -0.05125391 -0.29141679  0.37004027    0.00009317 -0.03242236  0.03158385    0.01342547 -0.02206211 -0.00343375

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.26726   0.53452   0.80178
Ly=   0.92212   0.09969  -0.37383
Lz=  -0.27975   0.83925  -0.46625

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.06724921 -0.08232684 -0.09121537    0.01000000  0.00000000  0.00000000   -0.01366667  0.00000000  0.00000000
 -0.08232683  0.21633101  0.14534362    0.00000000  0.04000000  0.00000000    0.00000000 -0.03066667  0.00000000
 -0.09121535  0.14534362  0.59044695    0.00000000  0.00000000  0.09000000    0.00000000  0.00000000  0.04433334

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   0.00000   0.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.00000   0.00000   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    0.00000   0.00000   0.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
 -1.366667 -0.766667  0.492593

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.00000000  0.00000000  0.00000000    0.01867778  0.00000000  0.00000000    0.01867778  0.00000000  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.02351111  0.00000000    0.00000000  0.02351111  0.00000000
  0.00000000  0.00000000  0.00000000    0.00000000  0.00000000  0.02183827    0.00000000  0.00000000  0.02183827

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base 
  0.04857142 -0.08232684 -0.09121538    0.04857143 -0.08232684 -0.09121537
 -0.08232684  0.19281989  0.14534362   -0.08232683  0.19281989  0.14534362
 -0.09121536  0.14534362  0.56860864   -0.09121535  0.14534362  0.56860870

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base 
  0.11000001 -0.05000000 -0.05000000    0.11000003 -0.05000000 -0.05000000
 -0.05000000  0.34999996 -0.28999996   -0.05000000  0.35000002 -0.28999996
 -0.05000000 -0.28999996  0.34999996   -0.05000002 -0.28999999  0.34999996

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.57735   0.57735   0.57735
Vy=   0.81650  -0.40825  -0.40825
Vz=   0.00000   0.70711  -0.70711

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base 
  0.01000000  0.00000000  0.00000000    0.01000002  0.00000000  0.00000001
  0.00000000  0.16000001  0.00000000    0.00000001  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005    0.00000006 -0.00000001  0.63999981
"""

getTLS3_test041 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 parallel to j : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 parallel to k : (wkx,wky,wkz)=    4.00000   1.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.500000 -0.300000  0.700000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   0.00000
   0.00000   0.00000   1.00000

modified shifts sx,sy,sz for the libration axes and the trace
 -1.366667 -0.766667  0.492593            0.056000  0.000000

principal Libration axes (orthonormal L base)
L1=   0.70711   0.70711   0.00000
L2=   0.00000   0.00000   1.00000
L3=   0.70711  -0.70711   0.00000

principal Vibration axes (orthonormal V base)
V1=   0.70711   0.70711   0.00000
V2=   0.00000   0.00000   1.00000
V3=   0.70711  -0.70711   0.00000

TLS matrices from Libration in the L-base
  0.26867777 -0.36000001  0.08000001    0.01000000  0.00000000  0.00000000   -0.01366667  0.03000000 -0.02000000
 -0.36000001  1.55351114 -0.06000000    0.00000000  0.04000000  0.00000000   -0.08000001 -0.03066667 -0.04000000
  0.08000001 -0.06000000  0.10183828    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.04433334
TLS matrices from Libration in the M-base
  0.26525804  0.08341976 -0.29698485    0.05000000 -0.04000000  0.00000000    0.05033333  0.02600000 -0.23334524
  0.08341974  0.10525802 -0.21213204   -0.04000000  0.05000000  0.00000000   -0.08400000 -0.01966666  0.27577165
 -0.29698485 -0.21213204  1.55351114    0.00000000  0.00000000  0.04000000   -0.08485281 -0.02828427 -0.03066667

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.32500002 -0.31500000  0.00000000
 -0.31500000  0.32500002  0.00000000
  0.00000000  0.00000000  0.16000001


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  0.59025806 -0.23158024 -0.29698485    0.05000000 -0.04000000  0.00000000    0.05033333  0.02600000 -0.23334524
 -0.23158026  0.43025804 -0.21213204   -0.04000000  0.05000000  0.00000000   -0.08400000 -0.01966666  0.27577165
 -0.29698485 -0.21213204  1.71351111    0.00000000  0.00000000  0.04000000   -0.08485281 -0.02828427 -0.03066667

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.70711   0.70711   0.00000
Ly=   0.00000   0.00000   1.00000
Lz=   0.70711  -0.70711   0.00000

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.27867779 -0.35999998  0.08000001    0.01000000  0.00000000  0.00000000   -0.01366667  0.03000000 -0.02000000
 -0.35999998  1.71351111 -0.05999999    0.00000000  0.04000000  0.00000000   -0.08000001 -0.03066667 -0.04000000
  0.08000002 -0.05999999  0.74183828    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.04433334

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    4.00000   1.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    2.12132  -2.12132   2.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=    0.70711  -2.12132   0.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    2.82843   2.82843   1.00000

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
 -1.366667 -0.766667  0.492593

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.25000000 -0.36000001  0.08000001    0.01867778  0.00000000  0.00000000    0.26867777 -0.36000001  0.08000001
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.02351111  0.00000000   -0.36000001  1.55351114 -0.06000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.02183827    0.08000001 -0.06000000  0.10183828

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base 
  0.01000003  0.00000000  0.00000000    0.01000002  0.00000003  0.00000001
  0.00000000  0.16000001  0.00000000    0.00000003  0.15999997  0.00000001
  0.00000001  0.00000000  0.63999999    0.00000001  0.00000001  0.63999999

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base 
  0.32500002 -0.31500000  0.00000000    0.32499999 -0.31499997  0.00000003
 -0.31500000  0.32500002  0.00000000   -0.31499997  0.32499999  0.00000002
  0.00000000  0.00000000  0.16000001    0.00000003  0.00000002  0.15999997

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.70711   0.70711   0.00000
Vy=   0.00000   0.00000   1.00000
Vz=   0.70711  -0.70711   0.00000

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base 
  0.01000000  0.00000000  0.00000000    0.01000002  0.00000003  0.00000000
  0.00000000  0.16000001  0.00000000    0.00000003  0.15999997  0.00000001
  0.00000000  0.00000000  0.64000005    0.00000000  0.00000001  0.63999993
"""

getTLS3_test044 = """\n
** control information -NOT FOR COMPARISON- SKIP IT**

rms and rms2 Libration around i,j,k
dx ,dy ,dz = 0.1000000 0.2000000 0.3000000
dx2,dy2,dz2= 0.0100000 0.0400000 0.0900000
vectors defining the principal Libration axes
   1.00000   2.00000   3.00000
   3.00000   1.00000   0.00000

rotation axes pass through the points in the L-system
 parallel to i : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 parallel to j : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 parallel to k : (wkx,wky,wkz)=    4.00000   1.00000   0.00000
correlation shifts sx,sy,sz for the libration axes
  0.500000 -0.300000  0.700000

rms and rms2 Vibration along x,y,z
tx ,ty ,tz = 0.1000000 0.4000000 0.8000000
tx2,ty2,tz2= 0.0100000 0.1600000 0.6400000
vectors defining the principal Vibration axes
   1.00000   1.00000   1.00000
   1.00000   0.00000   0.00000

modified shifts sx,sy,sz for the libration axes and the trace
 -1.366667 -0.766667  0.492593            0.056000  0.000000

principal Libration axes (orthonormal L base)
L1=   0.26726   0.53452   0.80178
L2=   0.92212   0.09969  -0.37383
L3=  -0.27975   0.83925  -0.46625

principal Vibration axes (orthonormal V base)
V1=   0.57735   0.57735   0.57735
V2=   0.81650  -0.40825  -0.40825
V3=   0.00000   0.70711  -0.70711

TLS matrices from Libration in the L-base
  0.26867777 -0.36000001  0.08000001    0.01000000  0.00000000  0.00000000   -0.01366667  0.03000000 -0.02000000
 -0.36000001  1.55351114 -0.06000000    0.00000000  0.04000000  0.00000000   -0.08000001 -0.03066667 -0.04000000
  0.08000001 -0.06000000  0.10183828    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.04433334
TLS matrices from Libration in the M-base
  1.18967915 -0.06853300 -0.70325685    0.04177019 -0.01602484  0.00009317    0.06204721 -0.09267259 -0.08686541
 -0.06853301  0.18730368  0.11607221   -0.01602484  0.06664596 -0.03242236   -0.25683391  0.02228853  0.14590052
 -0.70325685  0.11607219  0.54704458    0.00009317 -0.03242236  0.03158385    0.18746558 -0.01028393 -0.08433574

V matrix from Vibration in the V-base
  0.01000000  0.00000000  0.00000000
  0.00000000  0.16000001  0.00000000
  0.00000000  0.00000000  0.64000005
V matrix from Vibration in the M-base
  0.11000001 -0.05000000 -0.05000000
 -0.05000000  0.34999996 -0.28999996
 -0.05000000 -0.28999996  0.34999996


************* INFORMATION FOR COMPARISON **********

***  T[M] L[M] S[M] *** total TLS matrices in the main base (initial information) ***
  1.29967916 -0.11853299 -0.75325686    0.04177019 -0.01602484  0.00009317    0.06204721 -0.09267259 -0.08686541
 -0.11853301  0.53730363 -0.17392775   -0.01602484  0.06664596 -0.03242236   -0.25683391  0.02228853  0.14590052
 -0.75325686 -0.17392777  0.89704454    0.00009317 -0.03242236  0.03158385    0.18746558 -0.01028393 -0.08433574

***  Lx Ly Lz       *** principal Libration axes (orthonormal L base)
Lx=   0.26726   0.53452   0.80178
Ly=   0.92212   0.09969  -0.37383
Lz=  -0.27975   0.83925  -0.46625

***  T[L] L[L] S[L] *** total TLS matrices in the L base ***
  0.31724912 -0.44232687 -0.01121537    0.01000000  0.00000000  0.00000000   -0.01366667  0.03000000 -0.02000000
 -0.44232678  1.74633145  0.08534361    0.00000000  0.04000000  0.00000000   -0.08000001 -0.03066667 -0.04000000
 -0.01121539  0.08534359  0.67044687    0.00000000  0.00000000  0.09000000    0.09000000 -0.36000001  0.04433334

***  dx2 dy2 dz2     *** rms^2: Libration around lx,ly,lz
   0.0100000   0.0400000   0.0900000

***  dx  dy  dz      *** rms  : Libration around lx,ly,lz
   0.1000000   0.2000000   0.3000000

***  Wlx[L] Wly[L] Wlz[L] *** rotation axes pass through the points in the L-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    0.00000   2.00000   3.00000
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -1.00000   0.00000   2.00000
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    4.00000   1.00000   0.00000

***  Wlx[M] Wly[M] Wlz[M] *** rotation axes pass through the points in the M-base
 Wlx, axis parallel to lx : (wix,wiy,wiz)=    1.00499   2.71714  -2.14642
 Wly, axis parallel to ly : (wjx,wjy,wjz)=   -0.82676   1.14399  -1.73429
 Wlz, axis parallel to lz : (wkx,wky,wkz)=    1.99117   2.23778   2.83330

***  sx sy sz              *** correlation shifts sx,sy,sz for the libration axes
 -1.366667 -0.766667  0.492593

***  CW[L] CS[L] C[L]=CW[L]+CS[L] *** translation matrices from libration in the L base ***
  0.25000000 -0.36000001  0.08000001    0.01867778  0.00000000  0.00000000    0.26867777 -0.36000001  0.08000001
 -0.36000001  1.53000009 -0.06000000    0.00000000  0.02351111  0.00000000   -0.36000001  1.55351114 -0.06000000
  0.08000001 -0.06000000  0.08000001    0.00000000  0.00000000  0.02183827    0.08000001 -0.06000000  0.10183828

***  V[L]        V[L]=T[L]-C[L]     *** vibration matrix in the L-base 
  0.04857142 -0.08232684 -0.09121538    0.04857135 -0.08232686 -0.09121538
 -0.08232684  0.19281989  0.14534362   -0.08232677  0.19282031  0.14534362
 -0.09121536  0.14534362  0.56860864   -0.09121539  0.14534360  0.56860858

***  V[M]        V[M]=RML*VM*RMLtr     *** vibration matrix in the M-base 
  0.11000001 -0.05000000 -0.05000000    0.11000040 -0.04999991 -0.05000012
 -0.05000000  0.34999996 -0.28999996   -0.04999998  0.34999990 -0.28999999
 -0.05000000 -0.28999996  0.34999996   -0.05000018 -0.28999999  0.34999993

***  Vx Vy Vz       *** principal Vibration axes (orthonormal V base)
Vx=   0.57735   0.57735   0.57735
Vy=   0.81650  -0.40825  -0.40825
Vz=   0.00000   0.70711  -0.70711

***  V[V]        V[V]=RMVtr*VM*RMV  *** vibration matrix in the V-base 
  0.01000000  0.00000000  0.00000000    0.01000003  0.00000015  0.00000007
  0.00000000  0.16000001  0.00000000    0.00000025  0.16000028  0.00000013
  0.00000000  0.00000000  0.64000005    0.00000006  0.00000013  0.63999975
"""

def exercise_01():
  # getTLS3_test001.mes
  e = extract(s=getTLS3_test001)
  T = matrix.sym(sym_mat3=[0.01, 0.16, 0.64, 0,0,0])
  L = matrix.sym(sym_mat3=[0.01, 0.04, 0.09, 0,0,0])
  S = matrix.sqr([0,0,0,0,0,0,0,0,0])
  print_step("Input (getTLS3_test001.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  compare(e, r)

def exercise_04():
  # getTLS3_test004.mes
  e = extract(s=getTLS3_test004)
  T = matrix.sym(sym_mat3=[0.18685097, 0.45522982, 0.16791928,
                           -0.13412423, 0.03046584, -0.25211182])
  L = matrix.sym(sym_mat3=[0.01, 0.04, 0.09, 0,0,0])
  S = matrix.sqr([0,0,0,0,0,0,0,0,0])
  print_step("Input (getTLS3_test004.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)

def exercise_11():
  # getTLS3_test011.mes
  e = extract(s=getTLS3_test011)
  T = matrix.sym(sym_mat3=[0.32500002, 0.32500002, 0.16000001,
                           -0.315, 0,0])
  L = matrix.sym(sym_mat3=[0.05, 0.05, 0.04, -0.04, 0,0])
  S = matrix.sqr([0,0,0,0,0,0,0,0,0])
  print_step("Input (getTLS3_test011.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)

def exercise_14():
  # getTLS3_test014.mes
  e = extract(s=getTLS3_test014)
  T = matrix.sym(sym_mat3=[0.11, 0.35, 0.35,
                           -0.05, -0.05, -0.29])
  L = matrix.sym(sym_mat3=[0.04177019, 0.06664596, 0.03158385,
                           -0.01602484, 0.00009317, -0.03242236])
  S = matrix.sqr([0,0,0,0,0,0,0,0,0])
  print_step("Input (getTLS3_test014.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)

def exercise_21():
  # getTLS3_test021.mes
  e = extract(s=getTLS3_test021)
  T = matrix.sym(sym_mat3=[0.56999999, 0.41000003, 1.69000006,
                           -0.23, -0.29698485, -0.21213204])
  L = matrix.sym(sym_mat3=[0.05, 0.05, 0.04,
                           -0.04, 0, 0])
  S = matrix.sqr([0.035,       0.055,     -0.23334524,
                 -0.055,      -0.035,      0.27577165,
                 -0.08485281, -0.02828427, 0.0])
  print_step("Input (getTLS3_test021.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)

def exercise_24():
  # getTLS3_test024.mes
  e = extract(s=getTLS3_test024)
  T = matrix.sym(sym_mat3=[1.27664423,0.51635176,0.87700421,
                           -0.11823526,-0.75200295,-0.17251091])
  L = matrix.sym(sym_mat3=[0.04177019,0.06664596,0.03158385,
                           -0.01602484,0.00009317,-0.03242236])
  S = matrix.sqr([ 0.08563004, -0.07749246, -0.10029086,
                  -0.24165380, -0.00472804,  0.16796263,
                   0.17404011,  0.01177818, -0.08090200])
  print_step("Input (getTLS3_test024.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)
  
def exercise_31():
  # getTLS3_test031.mes
  e = extract(s=getTLS3_test031)
  T = matrix.sym(sym_mat3=[0.34525806,0.34525806,0.18351112,
                           -0.31658024,0,0])
  L = matrix.sym(sym_mat3=[0.05,0.05,0.04,-0.04,0,0])
  S = matrix.sqr([ 0.01533333, -0.02900000,  0.00000000,
                  -0.02900000,  0.01533333,  0.00000000,
                   0.00000000,  0.00000000, -0.03066667])
  print_step("Input (getTLS3_test031.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)
  
def exercise_34():
  # getTLS3_test034.mes
  e = extract(s=getTLS3_test034)
  T = matrix.sym(sym_mat3=[0.13303497,0.37095186,0.37004027,
                           -0.05029772,-0.05125391,-0.29141679])
  L = matrix.sym(sym_mat3=[0.04177019,0.06664596,0.03158385,
                           -0.01602484,0.00009317,-0.03242236])
  S = matrix.sqr([-0.02358282, -0.01518012,  0.01342547,
                  -0.01518013,  0.02701657, -0.02206211,
                   0.01342547, -0.02206211, -0.00343375])
  print_step("Input (getTLS3_test034.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)
  
def exercise_41():
  # getTLS3_test041.mes
  e = extract(s=getTLS3_test041)
  T = matrix.sym(sym_mat3=[0.59025806,0.43025804,1.71351111,
                           -0.23158024,-0.29698485,-0.21213204])
  L = matrix.sym(sym_mat3=[0.05,0.05,0.04,
                           -0.04,0,0])
  S = matrix.sqr([ 0.05033333,  0.02600000, -0.23334524,
                  -0.08400000, -0.01966666,  0.27577165,
                  -0.08485281, -0.02828427, -0.03066667])
  print_step("Input (getTLS3_test041.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)
  
def exercise_44():
  # getTLS3_test044.mes
  e = extract(s=getTLS3_test044)
  T = matrix.sym(sym_mat3=[1.29967916,0.53730363,0.89704454,
                          -0.11853299,-0.75325686,-0.17392775])
  L = matrix.sym(sym_mat3=[0.04177019,0.06664596,0.03158385,
                          -0.01602484,0.00009317,-0.03242236])
  S = matrix.sqr([ 0.06204721, -0.09267259, -0.08686541,
                  -0.25683391,  0.02228853,  0.14590052,
                   0.18746558, -0.01028393, -0.08433574])
  print_step("Input (getTLS3_test044.mes):")
  print "  T_M:\n", T
  print "  L_M:\n", L
  print "  S_M:\n", S
  r = tls_as_xyz.decompose_tls(T=T, L=L, S=S)
  print
  compare(e, r)


if (__name__ == "__main__"):
  exercise_01()
  exercise_04()
  exercise_11()
  exercise_14()
  exercise_21()
  #
  exercise_24()
  exercise_31()
  exercise_34()
  exercise_41()
  exercise_44()
