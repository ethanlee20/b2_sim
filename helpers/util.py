from typing import Any
from itertools import product
from math import prod
from dataclasses import dataclass, asdict, field, fields, is_dataclass
from copy import deepcopy
from pathlib import Path
from json import load, dump


def product_combine(d: dict[Any, list | tuple]):
    prod = product(*d.values())
    out = [dict(zip(d.keys(), i)) for i in prod]
    return out


def safer_convert_to_int(
    x: float,
) -> int:
    assert x.is_integer()
    return int(x)


def load_json(
    path: Path | str,
) -> dict:

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError
    with open(path, "r") as f:
        out = load(f)
    return out


def dump_json(
    obj: dict,
    path: Path | str,
) -> None:
    path = Path(path)
    with open(path, "x") as f:
        return dump(
            obj,
            f,
            indent=4,
        )


def read_from_nested_dict(dict_, keys: list):
    for key in keys:
        dict_ = dict_[key]
    return dict_


def write_to_nested_dict(dict_, keys: list, value):
    dict_ = read_from_nested_dict(dict_, keys[:-1])
    dict_[keys[-1]] = value


def _rebuild_dataclass(cls, dict_: dict, keys: list | None = None):
    if not is_dataclass(cls):
        return
    if keys is None:
        keys = []
    for field_ in fields(cls):
        _rebuild_dataclass(field_.type, dict_, keys=keys + [field_.name])
    if keys == []:
        out = cls(**dict_)
        return out
    write_to_nested_dict(dict_, keys, cls(**read_from_nested_dict(dict_, keys)))


def rebuild_dataclass(cls, dict_: dict):
    """
    dict_ must not contain dataclasses.
    """
    dict_ = deepcopy(dict_)
    out = _rebuild_dataclass(cls, dict_)
    return out


def load_dataclass_from_json_file(cls: Any, path: Path | str):
    dict_ = load_json(path)
    out = rebuild_dataclass(cls, dict_)
    return out


def save_dataclass_to_json_file(obj, path):
    dict_ = asdict(obj)
    dump_json(dict_, path)


def linspace(start: float, stop: float, num_points: int) -> list[float, ...]:
    if num_points < 1:
        raise ValueError("Need at least two points." f" Got: {num_points} points")
    if num_points == 1:
        if start != stop:
            raise ValueError("If creating only one point, start must equal stop.")
        out = [
            start,
        ]
        return out
    num_spaces = num_points - 1
    spacing = (stop - start) / num_spaces
    out = [start + i * spacing for i in range(num_points)]
    assert len(out) == num_points
    assert out[-1] == stop
    return out


@dataclass
class Interval:
    left: float
    right: float

    def as_tuple(self):
        return (self.left, self.right)

    def __iter__(self):
        tuple_ = self.as_tuple()
        out = tuple_.__iter__()
        return out


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
    num_total_events: int
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
        out = safer_convert_to_int(self.num_total_events / self.num_trials)
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
