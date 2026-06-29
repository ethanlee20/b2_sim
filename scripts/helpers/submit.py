from pathlib import Path
from subprocess import run
from time import sleep

from .util import ParameterValues, TrialMetadata, Paths


def read_dec_file(path: Path|str) -> str:
    with open(path, 'r', encoding="utf-8") as dec_file:
        out = dec_file.read()
    return out


def format_template_dec_file_string(str_:str, parameter_values:ParameterValues) -> str:
    format_map = dict(zip(parameter_values.names, parameter_values.values))
    try:
        out = str_.format(**format_map)
        return out
    except KeyError:
        raise ValueError("Not all decay file parameters were specified.")


def format_template_dec_file(path: Path|str, parameter_values: ParameterValues):
    text = read_dec_file(path)
    out = format_template_dec_file_string(text, parameter_values)
    return out


def write_formatted_dec_file(formatted_dec_file_path:Path|str, template_dec_file_path: Path|str, parameter_values:ParameterValues):
    formatted_dec_file_string = format_template_dec_file(template_dec_file_path, parameter_values)
    with open(formatted_dec_file_path, 'w') as formatted_dec_file:
        formatted_dec_file.write(formatted_dec_file_string)


def submit_job(
    num_events: int,
    sim_steer_file_path: Path|str,
    recon_steer_file_path: Path|str,
    decay_file_path: Path|str,
    sim_file_path: Path|str,
    recon_file_path: Path|str,
    log_file_path: Path|str,
    debug: bool = False,
) -> None:
    command = (
        f'bsub -q l "basf2 {sim_steer_file_path} -- {decay_file_path} {sim_file_path} {num_events} &>> {log_file_path}'
        f" && basf2 {recon_steer_file_path} {sim_file_path} {recon_file_path} &>> {log_file_path}"
        f' && rm {sim_file_path}"'
    )
    if debug:
        print(command, "\n")
        return
    run(
        command,
        shell=True,
    )


def trial_dir_is_incomplete(dir_path: Path|str) -> bool:
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


def find_incomplete_trial_dirs(dir_path: Path|str) -> list[Path]:
    dir_path = Path(dir_path)
    out = [
        child for child in dir_path.iterdir()
        if child.is_dir() and trial_dir_is_incomplete(child)
    ]
    return out


def submit_jobs(
    run_dir_path: Path|str,
    sim_steer_file_path: Path|str,
    recon_steer_file_path: Path|str,
    template_dec_file_path: Path|str,
    batch_size: int = 200,
    batch_wait_sec: int = 30,
    job_wait_sec: int | float = 0.1,
    debug: bool = False,
) -> None:

    submitted_job_count = 0

    incomplete_trial_dirs = find_incomplete_trial_dirs(run_dir_path)
    for trial_dir in incomplete_trial_dirs:
        trial_metadata = load_metadata_from_dir(TrialMetadata, trial_dir)
        trial_file_paths = FilePaths(trial_dir)
        write_formatted_dec_file(
            trial_file_paths.decay, template_dec_file_path, trial_metadata.parameter_values
        )
        for subtrial in range(trial_metadata.num_subtrials):
            _submit_job(
                num_events=trial_metadata.num_events_per_subtrial,
                sim_steer_file_path=sim_steer_file_path,
                recon_steer_file_path=recon_steer_file_path,
                decay_file_path=trial_file_paths.decay,
                sim_file_path=trial_file_paths.sim(subtrial),
                recon_file_path=trial_file_paths.recon(subtrial),
                log_file_path=trial_file_paths.log,
                debug=debug,
            )
            submitted_job_count += 1
            sleep(job_wait_sec)

            if submitted_job_count % batch_size == 0:
                sleep(batch_wait_sec)
