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


def data_dir(wc: int, split: str) -> Path:
    return Path(f"data/vary_one_large/vary_c{wc}_{split}/")


def dist(wc: int) -> Delta_WC_Intervals:
    if wc == 7:
        return Delta_WC_Intervals(
            dc7=Interval(-1, 1),
            dc9=Interval(0, 0),
            dc10=Interval(0, 0),
        )
    elif wc == 9:
        return Delta_WC_Intervals(
            dc7=Interval(0, 0),
            dc9=Interval(-10, 0),
            dc10=Interval(0, 0),
        )
    else:
        raise ValueError()


splits = ("train", "val")
wc_s = (7, 9)
num_trials = {"train": 200, "val": 10}
num_trial_events = {"train": 5_000, "val": 25_000}
num_subtrials = 1
lepton_flavor = "mu"


if run_setup:
    for wc, split in product(wc_s, splits):
        dist_ = dist(wc)
        dir_ = data_dir(wc, split)
        samples = Random_Sampler(dist_).sample(num_trials[split])
        setup_dir(
            dir_,
            samples,
            num_trial_events[split],
            num_subtrials,
            split,
            lepton_flavor,
            dist_,
        )
        if run_submit:
            submit_jobs(
                dir_,
                sim_steer_file_path,
                recon_steer_file_path,
                debug=debug,
            )
