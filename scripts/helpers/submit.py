from pathlib import Path
from subprocess import run
from time import sleep

from .util import Delta_WC_Values, Trial_Metadata, Paths


def write_dec_file(
    path: Path|str,
    lepton_flavor: str,
    delta_wc_values: DeltaWCValues,
) -> None:

    if lepton_flavor not in ("e", "mu"):
        raise ValueError(f"Lepton flavor must be 'e' or 'mu'.")

    content = f"""
    Alias MyB0 B0
    Alias MyAntiB0 anti-B0
    ChargeConj MyB0 MyAntiB0

    Alias MyK*0 K*0
    Alias MyAnti-K*0 anti-K*0
    ChargeConj MyK*0 MyAnti-K*0

    Decay Upsilon(4S)
    0.500  MyB0 anti-B0    VSS;
    0.500  B0 MyAntiB0    VSS;
    Enddecay

    Decay MyB0
    1.000 MyK*0 {lepton_flavor}+ {lepton_flavor}- BTOSLLNPR 0 0 {delta_wc_values.dc7} 0 1 {delta_wc_values.dc9} 0 2 {delta_wc_values.dc10} 0;
    Enddecay

    CDecay MyAntiB0

    Decay MyK*0
    1.000 K+ pi-   VSS;
    Enddecay

    CDecay MyAnti-K*0

    End
    """

    with open(path, "w") as file:
        file.write(content)


def submit_job(
    lepton_flavor: str,
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
        f" && basf2 {recon_steer_file_path} {lepton_flavor} {sim_file_path} {recon_file_path} &>> {log_file_path}"
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
    dir_path = Path(dir_path)
    trial_metadata = load_metadata_from_dir(TrialMetadata, dir_path)
    num_subtrials = trial_metadata.num_subtrials
    for subtrial in range(num_subtrials):
        recon_file_path = FilePaths(dir_path).recon(subtrial)
        if not recon_file_path.is_file():
            return True
    return False


def incomplete_trial_dirs(dir_path: Path|str) -> list[Path]:
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
    batch_size: int = 200,
    batch_wait_sec: int = 30,
    job_wait_sec: int | float = 0.1,
    debug: bool = False,
) -> None:

    submitted_job_count = 0
    for trial_dir in incomplete_trial_dirs(run_dir_path):
        trial_metadata = load_metadata_from_dir(TrialMetadata, trial_dir)
        trial_file_paths = FilePaths(trial_dir)
        write_dec_file(
            trial_file_paths.decay, trial_metadata.lepton_flavor, trial_metadata.delta_wc_values
        )
        for subtrial in range(trial_metadata.num_subtrials):
            _submit_job(
                trial_metadata.lepton_flavor,
                trial_metadata.num_events_per_subtrial,
                sim_steer_file_path,
                recon_steer_file_path,
                trial_file_paths.decay,
                trial_file_paths.sim(subtrial),
                trial_file_paths.recon(subtrial),
                trial_file_paths.log,
                debug=debug,
            )
            submitted_job_count += 1
            sleep(job_wait_sec)

            if submitted_job_count % batch_size == 0:
                sleep(batch_wait_sec)
