from pathlib import Path
from subprocess import run
from time import sleep

from .config import TrialMetadata, load_metadata_from_dir, FilePaths


def read_dec_file(path: Path | str) -> str:
    with open(path, "r", encoding="utf-8") as dec_file:
        out = dec_file.read()
    return out


def format_template_dec_file_string(
    str_: str, parameter_values: dict[str, float]
) -> str:
    for parameter_name in parameter_values.keys():
        if "{" f"{parameter_name}" "}" not in str_:
            raise ValueError(
                f"Parameter name not found in decay file string: {parameter_name}"
            )
    try:
        out = str_.format(**parameter_values)
        return out
    except KeyError:
        raise ValueError("Not all decay file parameters were specified?")


def format_template_dec_file(path: Path | str, parameter_values: dict[str, float]):
    text = read_dec_file(path)
    out = format_template_dec_file_string(text, parameter_values)
    return out


def write_formatted_dec_file(
    formatted_dec_file_path: Path | str,
    template_dec_file_path: Path | str,
    parameter_values: dict[str, float],
):
    formatted_dec_file_string = format_template_dec_file(
        template_dec_file_path, parameter_values
    )
    with open(formatted_dec_file_path, "w") as formatted_dec_file:
        formatted_dec_file.write(formatted_dec_file_string)


def make_sim_command_string(
    num_events: int,
    steer_file_path: Path | str,
    decay_file_path: Path | str,
    out_file_path: Path | str,
    log_file_path: Path | str,
):
    out = f"basf2 {steer_file_path} {decay_file_path} {out_file_path} {num_events} &>> {log_file_path}"
    return out


def make_recon_command_string(
    steer_file_path: Path | str,
    sim_file_path: Path | str,
    out_file_path: Path | str,
    log_file_path: Path | str,
):
    out = f"basf2 {steer_file_path} {sim_file_path} {out_file_path} &>> {log_file_path}"
    return out


def make_remove_sim_file_command_string(sim_file_path: Path | str):
    out = f"rm {sim_file_path}"
    return out


def make_bsub_command(
    num_events: int,
    sim_steer_file_path: Path | str,
    recon_steer_file_path: Path | str,
    decay_file_path: Path | str,
    sim_file_path: Path | str,
    recon_file_path: Path | str,
    log_file_path: Path | str,
    queue: str,
):
    sim_command = make_sim_command_string(
        num_events=num_events,
        steer_file_path=sim_steer_file_path,
        decay_file_path=decay_file_path,
        out_file_path=sim_file_path,
        log_file_path=log_file_path,
    )
    recon_command = make_recon_command_string(
        steer_file_path=recon_steer_file_path,
        sim_file_path=sim_file_path,
        out_file_path=recon_file_path,
        log_file_path=log_file_path,
    )
    remove_sim_file_command = make_remove_sim_file_command_string(
        sim_file_path=sim_file_path
    )

    out = f'bsub -q {queue} "{sim_command} && {recon_command} && {remove_sim_file_command}"'
    return out


def submit_job(
    num_events: int,
    sim_steer_file_path: Path | str,
    recon_steer_file_path: Path | str,
    decay_file_path: Path | str,
    sim_file_path: Path | str,
    recon_file_path: Path | str,
    log_file_path: Path | str,
    queue: str,
    debug: bool = False,
) -> None:
    command = make_bsub_command(
        num_events=num_events,
        sim_steer_file_path=sim_steer_file_path,
        recon_steer_file_path=recon_steer_file_path,
        decay_file_path=decay_file_path,
        sim_file_path=sim_file_path,
        recon_file_path=recon_file_path,
        log_file_path=log_file_path,
        queue=queue,
    )
    if debug:
        print(command)
        return
    run(command, shell=True)


def trial_dir_is_incomplete(dir_path: Path | str) -> bool:
    try:
        trial_metadata = load_metadata_from_dir(TrialMetadata, dir_path)
    except FileNotFoundError:
        raise RuntimeError(f"Trial directory does not contain metadata:\n{dir_path}")
    num_subtrials = trial_metadata.num_subtrials
    for subtrial in range(num_subtrials):
        recon_file_path = FilePaths(dir_path).recon(subtrial)
        if not recon_file_path.is_file():
            return True
    return False


def find_incomplete_trial_dirs(dir_path: Path | str) -> list[Path]:
    dir_path = Path(dir_path)
    out = [
        child
        for child in dir_path.iterdir()
        if child.is_dir() and trial_dir_is_incomplete(child)
    ]
    return out


def submit_jobs(
    run_dir: Path | str,
    sim_steer_file_path: Path | str,
    recon_steer_file_path: Path | str,
    template_dec_file_path: Path | str,
    queue: str = "l",
    batch_size: int = 200,
    batch_wait_sec: int = 30,
    job_wait_sec: int | float = 0.1,
    verbose: bool = True,
    debug: bool = False,
) -> None:
    """
    Submit jobs.

    Rerunning will skip trials deemed complete.
    """

    submitted_job_count = 0

    incomplete_trial_dirs = find_incomplete_trial_dirs(run_dir)

    for trial_dir in incomplete_trial_dirs:
        if verbose:
            print(f"Submitting jobs for {trial_dir}.")
        trial_metadata = load_metadata_from_dir(TrialMetadata, trial_dir)
        trial_file_paths = FilePaths(trial_dir)
        write_formatted_dec_file(
            trial_file_paths.decay,
            template_dec_file_path,
            trial_metadata.parameter_values,
        )
        for subtrial in range(trial_metadata.num_subtrials):
            submit_job(
                num_events=trial_metadata.num_events_per_subtrial,
                sim_steer_file_path=sim_steer_file_path,
                recon_steer_file_path=recon_steer_file_path,
                decay_file_path=trial_file_paths.decay,
                sim_file_path=trial_file_paths.sim(subtrial),
                recon_file_path=trial_file_paths.recon(subtrial),
                log_file_path=trial_file_paths.log,
                queue=queue,
                debug=debug,
            )
            submitted_job_count += 1
            sleep(job_wait_sec)

            if submitted_job_count % batch_size == 0:
                sleep(batch_wait_sec)
