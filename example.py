from helpers import (
    Interval,
    RunMetadata,
    setup_run_dir,
    submit_jobs,
)

# Setup

data_dir = "example/data/"

sim_steer_file_path = "example/steer_sim.py"
recon_steer_file_path = "example/steer_recon.py"
template_dec_file_path = "example/dec.dec"

parameter_bounds = {
    "dC_7": Interval(0, 0),
    "dC_9": Interval(-2, 1),
    "dC_10": Interval(0, 0),
}


# Create a training dataset by sampling from a grid of parameters

training_run_metadata = RunMetadata(
    split="train",
    total_num_events=10_000,
    num_trials=10,  # each trial represents a different parameter configuration
    num_subtrials_per_trial=1,
    parameter_bounds=parameter_bounds,
    sampling_type="grid",
    parameter_grid_counts={  # number of grid points along each axis
        "dC_7": 1,
        "dC_9": 10,
        "dC_10": 1,
    },
)

training_run_dir = setup_run_dir(
    run_metadata=training_run_metadata,
    parent_dir=data_dir,
)

submit_jobs(
    run_dir=training_run_dir,
    sim_steer_file_path=sim_steer_file_path,
    recon_steer_file_path=recon_steer_file_path,
    template_dec_file_path=template_dec_file_path,
    debug=True,
)


# Create a validation dataset by randomly sampling parameters

validation_run_metadata = RunMetadata(
    split="val",
    total_num_events=5_000,
    num_trials=5,
    num_subtrials_per_trial=2, # number of files per parameter value set
    parameter_bounds=parameter_bounds,
    sampling_type="random",
)

validation_run_dir = setup_run_dir(
    run_metadata=validation_run_metadata, parent_dir=data_dir
)

submit_jobs(
    run_dir=validation_run_dir,
    sim_steer_file_path=sim_steer_file_path,
    recon_steer_file_path=recon_steer_file_path,
    template_dec_file_path=template_dec_file_path,
    debug=True,
)
