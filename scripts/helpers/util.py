from typing import Any
from dataclasses import dataclass, asdict
from pathlib import Path
from json import load, dump
from types import FunctionType
from functools import cached_property


def load_json(
    path: Path|str,
) -> dict:

    path = Path(path)
    with open(path, "r") as f:
        return load(f)


def dump_json(
    obj: dict,
    path: Path|str,
) -> None:

    path = Path(path)
    with open(path, "x") as f:
        return dump(
            obj,
            f,
            indent=4,
        )


def safer_convert_to_int(
    x: float,
) -> int:
    assert x.is_integer()
    return int(x)


def linspace(start:float, stop:float, num_points: int) -> list[float]:
    if num_points < 1:
        raise ValueError("Need at least two points." f" Got: {num_points} points")
    num_spaces = num_points - 1
    spacing = (stop - start) / num_spaces
    out = [
        start + i * spacing
        for i in range(num_points)
    ]
    assert len(out) == num_points
    assert out[-1] == stop
    return out


@dataclass
class TrialMetadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    split: str
    lepton_flavor: str
    dC_7: float
    dC_9: float
    dC_10: float
    dC_7_bounds_left: float
    dC_7_bounds_right: float
    dC_9_bounds_left: float
    dC_9_bounds_right: float
    dC_10_bounds_left: float
    dC_10_bounds_right: float

    @property
    def num_events_per_subtrial(
        self,
    ) -> int:
        return safer_convert_to_int(self.num_events / self.num_subtrials)


def save_trial_metadata(metadata:TrialMetadata, path:Path|str) -> None:
    metadata_dict = asdict(metadata)
    dump_json(metadata_dict, path)


def load_trial_metadata(path:Path|str) -> TrialMetadata:

    metadata_dict = load_json(path)

    for key, cls in zip(
        ["delta_wc_set", "delta_wc_intervals"],
        [DeltaWCSet, DeltaWCIntervals],
    ):
        metadata_dict[key] = cls(**metadata_dict[key])

    return TrialMetadata(**metadata_dict)


@dataclass(frozen=True)
class Paths:
    dir_: Path
    metadata_file_name: str = "metadata.json"
    recon_file_name: FunctionType = lambda subtrial: f"recon_{subtrial}.root"
    sim_file_name: FunctionType = lambda subtrial: f"sim_{subtrial}.root"
    decay_file_name: str = "decay.dec"
    log_file_name: str = "log.log"

    @cached_property
    def metadata_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.metadata_file_name)

    def recon_file_path(self, subtrial: int) -> Path:
        recon_file_name = self.recon_file_name(subtrial)
        return self.dir_.joinpath(recon_file_name)

    def sim_file_path(
        self,
        subtrial: int,
    ) -> Path:
        sim_file_name = self.sim_file_name(subtrial)
        return self.dir_.joinpath(sim_file_name)

    @cached_property
    def decay_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.decay_file_name)

    @cached_property
    def log_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.log_file_name)
