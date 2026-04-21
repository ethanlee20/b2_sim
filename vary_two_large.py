
"""
Generate Standard Model events.
"""

from pathlib import Path
from itertools import product

from helpers import Random_Sampler, Delta_WC_Intervals, Interval, setup_dir, submit_jobs


run_setup = True
run_submit = True
debug = True

sim_steer_file_path = Path("steering/steer_sim.py")
recon_steer_file_path = Path("steering/steer_recon.py")

data_dir = lambda split: Path(f"data/vary_two_large/vary_c7_c9_{split}/")

dist = Delta_WC_Intervals(
    dc7=Interval(-1, 1),
    dc9=Interval(-10, 0),
    dc10=Interval(0, 0),
)

splits = ("train", "val")
num_trials = {"train": 200, "val": 20}
num_trial_events = {"train": 5_000, "val": 25_000}
num_subtrials = 1
lepton_flavor = "mu"


if run_setup:
    for split in splits:
        dir_ = data_dir(split)
        samples = (
            Random_Sampler(dist)
            .sample(num_trials[split])
        )
        setup_dir(
            dir_, 
            samples, 
            num_trial_events[split], 
            num_subtrials, 
            split, 
            lepton_flavor, 
            dist,
        )
        if run_submit:
            submit_jobs(
                dir_, 
                sim_steer_file_path, 
                recon_steer_file_path, 
                debug=debug,
            )