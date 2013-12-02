 # -*- coding: utf-8; py-indent-offset: 2 -*-
from __future__ import division

import os

# We must make sure to import sklearn before boost python
import sklearn.svm

import libtbx
from mmtbx.command_line.water_screen import master_phil
from mmtbx.ions.environment import ChemicalEnvironment, ScatteringEnvironment
from mmtbx import ions
from mmtbx.ions.svm import ion_class, ion_vector, predict_ion, get_classifier
from mmtbx.regression.make_fake_anomalous_data import generate_zinc_inputs
import mmtbx.command_line

def exercise () :
  if get_classifier() is None:
    print "Skipping {}".format(os.path.split(__file__)[1])
    return

  wavelength = 1.025
  mtz_file, pdb_file = generate_zinc_inputs(anonymize = False)
  null_out = libtbx.utils.null_out()

  cmdline = mmtbx.command_line.load_model_and_data(
    args = [pdb_file, mtz_file, "wavelength={}".format(wavelength),
            "use_phaser=True"],
    master_phil = master_phil(),
    out = null_out,
    process_pdb_file = True,
    create_fmodel = True,
    prefer_anomalous = True
    )

  os.remove(pdb_file)
  os.remove(mtz_file)
  os.remove(os.path.splitext(pdb_file)[0] + "_fmodel.eff")

  cmdline.xray_structure.set_inelastic_form_factors(
    photon = cmdline.params.wavelength,
    table = "sasaki"
    )

  cmdline.fmodel.update_xray_structure(
    cmdline.xray_structure,
    update_f_calc = True
    )

  manager = ions.create_manager(
    pdb_hierarchy = cmdline.pdb_hierarchy,
    fmodel = cmdline.fmodel,
    geometry_restraints_manager = cmdline.geometry,
    wavelength = cmdline.params.wavelength,
    params = cmdline.params,
    nproc = cmdline.params.nproc,
    log = null_out
    )

  manager.validate_ions(
    out = null_out
    )

  fo_map = manager.get_map("mFo")

  for atom_props in manager.atoms_to_props.values():
    chem_env = ChemicalEnvironment(
      atom_props.i_seq,
      manager.find_nearby_atoms(atom_props.i_seq, far_distance_cutoff = 3.5),
      manager
      )
    scatter_env = ScatteringEnvironment(
      atom_props.i_seq, manager, fo_map
      )
    resname = ion_class(chem_env)
    prediction = predict_ion(chem_env, scatter_env,
                             elements = ["ZN", "MN", "CA"])
    assert resname != ""
    assert resname == prediction[0][0]

  del fo_map

  print "OK"
if __name__ == "__main__":
  exercise()
