from typing import Any
from dataclasses import dataclass, asdict
from pathlib import Path
from json import load, dump
from types import FunctionType
from functools import cached_property


def safer_convert_to_int(
    x: float,
) -> int:
    assert x.is_integer()
    return int(x)


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


def read_nested_dict(dict_, keys: list):
    for key in keys:
        dict_ = dict_[key]
    return dict_


def write_nested_dict(dict_, keys:list, value):
    dict_ = read_nested_dict(dict_, keys[:-1])
    dict_[keys[-1]] = value


def _rebuild_dataclass(cls, dict_:dict, keys:list|None=None):
    if not is_dataclass(cls):
        return
    if keys is None:
        keys = []
    for field_ in fields(cls):
        _rebuild(field_.type, dict_, keys=keys+[field_.name])
    if keys == []:
        out = cls(**dict_)
        return out
    write_nested_dict(dict_, keys, cls(**read_nested_dict(dict_, keys)))


def rebuild_dataclass(cls, dict_:dict):
    dict_ = deepcopy(dict_)
    out = _rebuild(cls, dict_)
    return out


def load_dataclass_from_json_file(cls: Any, path: Path|str):
    dict_ = load_json(path)
    out = rebuild_dataclass(cls, dict_)
    return out


def save_dataclass_to_json_file(obj, path):
    dict_ = asdict(obj)
    dump_json(dict_, path)


def linspace(start:float, stop:float, num_points: int) -> list[float, ...]:
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
Interval:
    left: float
    right: float

    def as_tuple(self):
        return (self.left, self.right)

    def __iter__(self):
        tuple_ = self.as_tuple()
        out = tuple_.__iter__()
        return out


@dataclass
class DeltaWCBase:
    dC_7: Any
    dC_9: Any
    dC_10: Any

    def as_tuple(self):
        out = (dC_7, dC_9, dC_10)
        return out

    def __iter__(self):
        tuple_ = self.as_tuple()
        out = tuple_.__iter__()
        return out


@dataclass
class DeltaWCValues(DeltaWCBase):
    dC_7: float
    dC_9: float
    dC_10: float


@dataclass
class DeltaWCBounds(DeltaWCBase):
    dC_7: Interval
    dC_9: Interval
    dC_10: Interval


@dataclass
class DeltaWCCounts(DeltaWCBase):
    dC_7: int
    dC_9: int
    dC_10: int


@dataclass
class Filenames:
    metadata: Path|str = "metadata.json"
    decay: Path|str = "decay.dec"
    log: Path|str = "log.log"

    @property
    def recon(self, subtrial:int):
        out = f"recon_{subtrial}.root"
        return out

    @property
    def sim(self, subtrial:int):
        out = f"sim_{subtrial}.root"
        return out


@dataclass
class FilePaths:
    dir_: Path|str
    metadata: Path = field(init=False)
    decay: Path = field(init=False)
    log: Path = field(init=False)
    
    def __post_init__(self):
        self.dir_ = Path(self.dir_)
        filenames = Filenames()
        self.metadata = self.dir_.joinpath(filenames.metadata)
        self.decay = self.dir_.joinpath(filenames.decay)
        self.log = self.dir_.joinpath(filenames.log)

    @property
    def recon(self, subtrial:int):
        filename = Filenames().recon(subtrial)
        out = self.dir_.joinpath(filename)
        return out
    
    @property
    def sim(self, subtrial:int):
        filename = Filenames().sim(subtrial)
        out = self.dir_.joinpath(filename)
        return out


@dataclass
class SubtrialMetadata:
    subtrial_num: int
    num_events: int
    delta_wc_values: DeltaWCValues
    lepton_flavor: str


@dataclass
class TrialMetadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    delta_wc_values: DeltaWCValues
    lepton_flavor: str

    @property
    def num_events_per_subtrial(self):
        out = safer_convert_to_int(num_events / num_subtrials)
        return out


@dataclass
class RunMetadata:
    split: str
    num_events: int
    num_trials: int
    num_subtrials_per_trial: int
    lepton_flavor: str
    delta_wc_bounds: DeltaWCBounds

    @property
    def num_events_per_trial(self):
        out = safer_convert_to_int(self.num_events / self.num_trials)
        return out

    @property
    def num_events_per_subtrial(self):
        out = safer_convert_to_int(self.num_events_per_trial/ self.num_subtrials_per_trial)


def make_trial_metadata_list(run_metadata: RunMetadata, delta_wc_values_list:list[DeltaWCValues]):
    out = [
        TrialMetadata(trial_num, run_metadata.num_events_per_trial, run_metadata.num_subtrials_per_trial, delta_wc_values, run_metadata.lepton_flavor) 
        for trial_num, delta_wc_values in enumerate(delta_wc_values_list)
    ] 
    return out


def save_metadata_to_dir(metadata:TrialMetadata|RunMetadata, dir_path:Path|str) -> None:
    dir_path = Path(dir_path)
    filename = Filenames().metadata
    path = dir_path.joinpath(filename)
    save_dataclass_to_json_file(metadata, path)


def load_metadata_from_dir(metadata_cls, dir_path:Path|str) -> RunMetadata|TrialMetadata:
    dir_path = Path(dir_path)
    filename = Filenames().metadata
    path = dir_path.joinpath(filename)
    out = load_dataclass_from_json_file(metadata_cls, path)
    return out 
    

