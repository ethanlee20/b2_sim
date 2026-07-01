from helpers import (
    Interval,
    RunMetadata,
    GridSampler,
    RandomSampler,
    setup_run_dir,
    submit_jobs,
)

# training dataset simulation run

training_run_metadata = RunMetadata(
    split="train",
    num_events=10_000,
    num_trials=10,
    num_subtrials_per_trial=1,
    parameter_bounds={
        "dC_7": Interval(0, 0),
        "dC_9": Interval(-2, 1),
        "dC_10": Interval(0, 0),
    },
)

training_grid_sampler = GridSampler(training_run_metadata.parameter_bounds)

training_parameter_values = training_grid_sampler.sample(
    parameter_counts={"dC_7": 1, "dC_9": 10, "dC_10": 1}
)

training_run_dir_path = setup_run_dir(
    run_metadata=training_run_metadata,
    parameter_values=training_parameter_values,
    parent_dir_path="example/data/",
)

submit_jobs(
    run_dir_path=training_run_dir_path,
    sim_steer_file_path="example/steer_sim.py",
    recon_steer_file_path="example/steer_recon.py",
    template_dec_file_path="example/dec.dec",
    queue="l",
    batch_size=200,
    batch_wait_sec=30,
    job_wait_sec=0.1,
    debug=False,
)


# validation dataset simulation run

validation_run_metadata = RunMetadata(
    split="val",
    num_events=5_000,
    num_trials=5,
    num_subtrials_per_trial=1,
    parameter_bounds={
        "dC_7": Interval(0, 0),
        "dC_9": Interval(-2, 1),
        "dC_10": Interval(0, 0),
    },
)

validation_random_sampler = RandomSampler(validation_run_metadata.parameter_bounds)

validation_parameter_values = validation_random_sampler.sample(
    n=validation_run_metadata.num_trials
)

validation_run_dir_path = setup_run_dir(
    run_metadata=validation_run_metadata,
    parameter_values=validation_parameter_values,
    parent_dir_path="example/data/",
)

submit_jobs(
    run_dir_path=validation_run_dir_path,
    sim_steer_file_path="example/steer_sim.py",
    recon_steer_file_path="example/steer_recon.py",
    template_dec_file_path="example/dec.dec",
    queue="l",
    batch_size=200,
    batch_wait_sec=30,
    job_wait_sec=0.1,
    debug=False,
)
