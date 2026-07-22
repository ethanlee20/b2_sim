from pathlib import Path
from dataclasses import dataclass, field

from .util import Interval, load_dataclass_from_json_file, save_dataclass_to_json_file


@dataclass
class Filenames:
    metadata: Path | str = "metadata.json"
    decay: Path | str = "decay.dec"
    log: Path | str = "log.log"

    def recon(self, subtrial: int):
        out = f"recon_{subtrial}.root"
        return out

    def sim(self, subtrial: int):
        out = f"sim_{subtrial}.root"
        return out


@dataclass
class FilePaths:
    dir_: Path | str
    metadata: Path = field(init=False)
    decay: Path = field(init=False)
    log: Path = field(init=False)

    def __post_init__(self):
        self.dir_ = Path(self.dir_)
        filenames = Filenames()
        self.metadata = self.dir_.joinpath(filenames.metadata)
        self.decay = self.dir_.joinpath(filenames.decay)
        self.log = self.dir_.joinpath(filenames.log)

    def recon(self, subtrial: int):
        filename = Filenames().recon(subtrial)
        out = self.dir_.joinpath(filename)
        return out

    def sim(self, subtrial: int):
        filename = Filenames().sim(subtrial)
        out = self.dir_.joinpath(filename)
        return out


@dataclass
class SubtrialMetadata:
    subtrial_num: int
    num_events: int
    parameter_values: dict[str, float]


@dataclass
class TrialMetadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    parameter_values: dict[str, float]

    @property
    def num_events_per_subtrial(self) -> int:
        out = safer_convert_to_int(self.num_events / self.num_subtrials)
        return out


@dataclass
class RunMetadata:
    split: str
    total_num_events: int
    num_trials: int
    num_subtrials_per_trial: int
    parameter_bounds: dict[str, Interval]
    sampling_type: str
    parameter_grid_counts: None | dict[str, int] = None

    def __post_init__(self):
        if self.sampling_type not in ("grid", "random"):
            raise ValueError
        if self.sampling_type == "grid" and self.parameter_grid_counts is None:
            raise ValueError
        if self.sampling_type != "grid" and self.parameter_grid_counts is not None:
            raise ValueError
        if (
            self.parameter_grid_counts is not None
            and self.total_num_grid_points != self.num_trials
        ):
            raise ValueError

    @property
    def num_events_per_trial(self) -> int:
        out = safer_convert_to_int(self.total_num_events / self.num_trials)
        return out

    @property
    def num_events_per_subtrial(self) -> int:
        out = safer_convert_to_int(
            self.num_events_per_trial / self.num_subtrials_per_trial
        )
        return out

    @property
    def total_num_grid_points(self) -> None | int:
        if self.parameter_grid_counts is None:
            return None
        out = prod(self.parameter_grid_counts.values())
        return out


def make_trial_metadata_list(
    run_metadata: RunMetadata, parameter_values_list: list[dict[str, float]]
) -> list[TrialMetadata]:
    assert len(parameter_values_list) == run_metadata.num_trials
    out = [
        TrialMetadata(
            trial_num,
            run_metadata.num_events_per_trial,
            run_metadata.num_subtrials_per_trial,
            parameter_values,
        )
        for trial_num, parameter_values in enumerate(parameter_values_list)
    ]
    return out


def save_metadata_to_dir(
    metadata: TrialMetadata | RunMetadata, dir_path: Path | str
) -> None:
    dir_path = Path(dir_path)
    filename = Filenames().metadata
    path = dir_path.joinpath(filename)
    save_dataclass_to_json_file(metadata, path)


def load_metadata_from_dir(
    metadata_cls, dir_path: Path | str
) -> RunMetadata | TrialMetadata:
    dir_path = Path(dir_path)
    filename = Filenames().metadata
    path = dir_path.joinpath(filename)
    out = load_dataclass_from_json_file(metadata_cls, path)
    return out
