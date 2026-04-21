
"""
Generate Standard Model events!
"""

from pathlib import Path

from helpers import Random_Sampler, Delta_WC_Intervals, Interval, setup_dir, submit_jobs


run_setup = True
run_submit = True
debug = True

sim_steer_file_path = Path("steering/steer_sim.py")
recon_steer_file_path = Path("steering/steer_recon.py")
data_dir = Path("data/sm")

dist = Delta_WC_Intervals(
    dc7=Interval(0, 0), 
    dc9=Interval(0, 0), 
    dc10=Interval(0, 0),
)

num_trials = 30
num_trial_events = 10_000
num_subtrials = 1
split = "_"
lepton_flavor = "mu"


if run_setup:
    samples = (
        Random_Sampler(dist)
        .sample(num_trials)
    )
    setup_dir(
        data_dir, 
        samples, 
        num_trial_events, 
        num_subtrials, 
        split, 
        lepton_flavor, 
        dist,
    )
if run_submit:
    submit_jobs(
        data_dir, 
        sim_steer_file_path, 
        recon_steer_file_path, 
        debug=debug
    )