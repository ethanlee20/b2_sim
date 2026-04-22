
from pathlib import Path
from subprocess import run
from time import sleep

from .util import Delta_WC_Values, Trial_Metadata, Paths


def _write_dec_file(
    path: Path, 
    lepton_flavor: str, 
    delta_wc_values: Delta_WC_Values, 
) -> None:
    
    if lepton_flavor not in ("e", "mu"):
        raise ValueError(
            f"Lepton flavor ({lepton_flavor})" 
            " must be 'e' or 'mu'."
        )
    
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


def _submit_job(
    lepton_flavor:str,
    num_events:int,
    sim_steer_file_path:Path,
    recon_steer_file_path:Path,
    decay_file_path:Path,
    sim_file_path:Path,
    recon_file_path:Path,
    log_file_path:Path,
    debug:bool=False,
) -> None:
    command = (
        f'bsub -q l "basf2 {sim_steer_file_path} -- {decay_file_path} {sim_file_path} {num_events} &>> {log_file_path}'
        f' && basf2 {recon_steer_file_path} {lepton_flavor} {sim_file_path} {recon_file_path} &>> {log_file_path}'
        f' && rm {sim_file_path}"'
    )
    if debug:
        print(command, '\n')
        return
    run(
        command,
        shell=True,
    )


def _trial_dir_is_incomplete(
    dir_:Path,
) -> bool:
    num_subtrials = Trial_Metadata.from_json_file(
        Paths(dir_).metadata_file_path
    ).num_subtrials
    num_recon_files = len(
        list(dir_.glob(Paths.recon_file_name("*")))
    )
    if num_subtrials != num_recon_files:
        return True
    return False


def _get_incomplete_trial_dirs(
    dir_:Path
) -> list[Path]:
    return [
        p.parent
        for p in dir_.rglob(Paths.metadata_file_name)
        if _trial_dir_is_incomplete(p.parent)
    ]


def submit_jobs(
    dir_:Path,
    sim_steer_file_path:Path,
    recon_steer_file_path:Path,
    batch_size:int=250, 
    batch_wait:int=120,
    job_wait:int|float=0.1,
    debug:bool=False,
) -> None:
    if not dir_.is_dir():
        raise ValueError(
            "Data directory is not directory:"
            f" ({dir_})."
        )
    num_submitted_jobs = 0
    for p in _get_incomplete_trial_dirs(dir_):
        paths = Paths(p)
        metadata = Trial_Metadata.from_json_file(
            paths.metadata_file_path
        )
        _write_dec_file(
            paths.decay_file_path, 
            metadata.lepton_flavor, 
            metadata.delta_wc_values
        )
        for subtrial in range(metadata.num_subtrials):
            _submit_job(
                metadata.lepton_flavor,
                metadata.num_events_per_subtrial,
                sim_steer_file_path,
                recon_steer_file_path,
                paths.decay_file_path,
                paths.sim_file_path(subtrial),
                paths.recon_file_path(subtrial),
                paths.log_file_path,
                debug=debug,
            )
            num_submitted_jobs += 1
            sleep(job_wait)

            if num_submitted_jobs % batch_size == 0:
                sleep(batch_wait)
