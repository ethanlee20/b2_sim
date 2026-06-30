from helpers import RunMetadata, GridSampler, RandomSampler, setup_run_dir, submit_jobs

run_metadata = RunMetadata(
    split="train",
    num_events=10_000,
    num_trials=10,
    num_subtrials_per_trial=1,
    parameter_bounds={"dC_7": (0, 0), "dC_9": (-2, 1), "dC_10": (0, 0)},
)

grid_sampler = GridSampler(run_metadata.parameter_bounds)

parameter_values_list = grid_sampler.sample(
    parameter_counts={"dC_7": 1, "dC_9": 10, "dC_10": 1}
)

run_dir_path = setup_run_dir(
    run_metadata=run_metadata,
    parameter_values_list=parameter_values_list,
    parent_dir_path="example/data",
)

submit_jobs(
    run_dir_path=run_dir_path,
    sim_steer_file_path="example/generator_sim_steer.py",
    recon_steer_file_path="example/btokstarmumu_generator_recon_steer.py",
    template_dec_file_path="example/btokstarmumu.dec",
    queue="l",
    batch_size=200,
    batch_wait_sec=30,
    job_wait_sec=0.1,
    debug=True,
)
