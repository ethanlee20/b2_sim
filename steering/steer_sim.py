#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import basf2 as b2
import simulation as si
import reconstruction as re
import mdst as mdst
import glob as glob

path_file_dec = sys.argv[1]
path_file_out = sys.argv[2]
n_events = int(sys.argv[3])

print("\n-- Simulation Configuration --")
print(f"Decay file: {path_file_dec}")
print(f"Output file: {path_file_out}")
print(f"Number of events: {n_events}")
print("-----------------------\n")

# background (collision) files
bg = glob.glob(
    "/group/belle2/dataprod/BGOverlay/early_phase3/release-06-00-05/overlay/BGx1/set0/*.root"
)
# background if running locally
bg_local = glob.glob(
    "/group/belle2/dataprod/BGOverlay/early_phase3/release-06-00-05/overlay/BGx1/set0/*.root"
)

# set database conditions (in addition to default)
b2.conditions.prepend_globaltag("mc_production_MC15ri_a")

print("Create path")
main = b2.Path()

# default to early phase 3 (exp=1003), run 0
print("Add EventInfoSetter")
main.add_module("EventInfoSetter", expList=1003, runList=0, evtNumList=n_events)

# generate events from decfile
print("Add EvtGenInput")
main.add_module("EvtGenInput", userDECFile=b2.find_file(path_file_dec))

# detector simulation
# print("Add simulation")
# si.add_simulation(path=main, bkgfiles=bg)

# reconstruction
# print("Add reconstruction")
# re.add_reconstruction(path=main)

# Finally add mdst output (file name overwritten on the grid)
print("Add mdst output")
mdst.add_mdst_output(path=main, filename=str(path_file_out))

# process events and print call statistics
print("Process")
b2.process(path=main)
print(b2.statistics)
