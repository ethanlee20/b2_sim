
from pathlib import Path

from helpers import (
    Grid_Sampler, 
    Random_Sampler,
    Delta_WC_Intervals, 
    Delta_WC_Counts,
    Interval, 
    setup_dir, 
    submit_jobs,
)


run_setup = True
run_submit = True
debug = False

data_dir = lambda split : Path(f"data/vary_two_large_grid/vary_dc7_dc9_{split}")

sim_steer_file_path = Path("steering/steer_sim.py")
recon_steer_file_path = Path("steering/steer_recon.py")

num_events_per_trial = {"train": 100_000, "val": 25_000}
num_subtrials_per_trial = 1
lepton_flavor = "mu"

intervals = Delta_WC_Intervals(
    dc7=Interval(-0.1, 0.1),
    dc9=Interval(-10, 0),
    dc10=Interval(0, 0),
)

samplers = {
   "train": Grid_Sampler(intervals),
   "val": Random_Sampler(intervals),
}

counts = {
    "train": Delta_WC_Counts(
        dc7=10,
        dc9=10,
        dc10=1,
    ),
    "val": 10,
}

samples = {
    split : sampler.sample(counts[split])
    for split, sampler in samplers.items()
}

for split, samples_ in samples.items():
    dir_ = data_dir(split)
    if run_setup:
        setup_dir(
            dir_, 
            samples_, 
            num_events_per_trial[split], 
            num_subtrials_per_trial, 
            split, 
            lepton_flavor, 
            intervals,
        )
    if run_submit:
        submit_jobs(
            dir_, 
            sim_steer_file_path, 
            recon_steer_file_path, 
            debug=debug,
        )