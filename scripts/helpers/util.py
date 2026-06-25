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
Interval:
    left: float
    right: float

    @classmethod
    def from_dict(cls, dict_):
        dict_ = {
            dict_[field_.name]: field_.type(dict_[field_.name]) 
            for field_ in fields(cls)
        }
        out = cls(**dict_)
        return out

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
class TrialMetadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    delta_wc_values: DeltaWCValues


@dataclass
class RunMetadata:
    num_events: int
    num_trials: int
    split: str
    lepton_flavor: str
    delta_wc_bounds: DeltaWCBounds


@dataclass
class Filenames:
    metadata: Path|str = "metadata.json"
    decay: Path|str = "decay.dec"
    log: Path|str

    @property
    def recon(self, subtrial:int):
        out = f"recon_{subtrial}.root"
        return out

    @property
    def sim(self, subtrial:int):
        out = f"sim_{subtrial}.root"
        return out


"""
@dataclass
class TrialFilePaths:
    dir_: Path|str
    filenames: Filenames = field(default_factory=Filenames, )

    @property
    def decay(self):
        out = make_path(filenames.decay)
        return out

    @property
    def metadata_file_path(self):
        metadata_filename = "metadata.json"
        out = self.dir_.joinpath(metadata_filename)
        return out

    def recon_filename(self, subtrial:int):
        out = f"recon_{subtrial}.root"
        return out
        
    def sim_filename(self, subtrial:int):
        out = f"sim_{subtrial}.root"
        return out

    def make_path(self, filename):
        out = self.dir_.joinpath(filename)
        return out
    
    def __post_init__(self):
        self.dir_ = Path(self.dir_)
"""