#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# based off of Alexei's steering file


import sys

import basf2 as b2
import mdst as mdst
import glob as glob

dec_file_path = sys.argv[1]
out_file_path = sys.argv[2]
num_events = int(sys.argv[3])

print("\n-- Simulation Configuration --")
print(f"Decay file: {dec_file_path}")
print(f"Output file: {out_file_path}")
print(f"Number of events: {num_events}")
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
main.add_module("EventInfoSetter", expList=1003, runList=0, evtNumList=num_events)

# generate events from decfile
print("Add EvtGenInput")
main.add_module("EvtGenInput", userDECFile=b2.find_file(dec_file_path))

# Finally add mdst output (file name overwritten on the grid)
print("Add mdst output")
mdst.add_mdst_output(path=main, filename=str(out_file_path))

# process events and print call statistics
print("Process")
b2.process(path=main)
print(b2.statistics)
