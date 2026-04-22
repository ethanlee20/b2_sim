
from typing import Any
from dataclasses import dataclass, asdict
from pathlib import Path
from json import load, dump
from types import FunctionType
from functools import cached_property


def load_json(
    path: Path,
)-> dict:
    with open(path, 'r') as f:
        return load(f)


def dump_json(
    obj: dict,
    path: Path,
) -> None:
    with open(path, 'x') as f:
        return dump(
            obj, 
            f, 
            indent=4,
        )


def safer_convert_to_int(
    x:float,
) -> int:
    assert x.is_integer()
    return int(x)


@dataclass
class Interval:
    left:float
    right:float
    
    def __post_init__(
        self
    ):
        if self.left > self.right:
            raise ValueError(
                "Interval left bound must be greater" 
                " than or equal to right bound."
            )
        self.is_degenerate = (self.left == self.right)
        
    def __iter__(
        self,
    ):
        return (
            self.left, 
            self.right,
        ).__iter__()


def linspace(
    interval:Interval, 
    num_points:int
) -> list:
    if num_points < 1:
        raise ValueError(
            "Need at least one point."
            f" Got: {num_points}"
        )
    if num_points == 1 and not interval.is_degenerate:
        raise ValueError(
            "Can have one point only if interval is degenerate."
            " i.e. left bound == right bound."
        )
    if num_points == 1:
        return [float(interval.left)]
    num_spaces = num_points - 1
    spacing = (
        (interval.right - interval.left) 
        / num_spaces
    )
    array_ = []
    for i in range(num_points):
        point = (
            interval.left 
            + i * spacing
        )
        array_.append(point)
    return array_


@dataclass(frozen=True)
class Delta_WC_Info:
    dc7: Any
    dc9: Any
    dc10: Any
    
    def __iter__(self):
        return (
            self.dc7,
            self.dc9,
            self.dc10,
        ).__iter__()


@dataclass(frozen=True)
class Delta_WC_Values(Delta_WC_Info):
    dc7: float
    dc9: float
    dc10: float


@dataclass(frozen=True)
class Delta_WC_Counts(Delta_WC_Info):
    dc7: int
    dc9: int
    dc10: int


@dataclass(frozen=True)
class Delta_WC_Intervals(Delta_WC_Info):
    dc7: Interval 
    dc9: Interval 
    dc10: Interval 


@dataclass
class Metadata:
    trial_num: int
    num_events: int
    num_subtrials: int
    split: str
    lepton_flavor: str
    delta_wc_values: Delta_WC_Values
    delta_wc_intervals: Delta_WC_Intervals

    @property
    def num_subtrial_events(
        self,
    ) -> int:
        return safer_convert_to_int(
            self.num_events
            / self.num_subtrials
        )
    
    def to_json_file(
        self, 
        path,
    ) -> None:
        dump_json(
            asdict(self), 
            path,
        )

    @classmethod
    def from_json_file(
        cls, 
        path:Path,
    ):
        dict_ = load_json(path)
        for key, cls_ in zip(
            ["delta_wc_values", "delta_wc_intervals"], 
            [Delta_WC_Values, Delta_WC_Intervals],
        ):
            dict_[key] = cls_(**dict_[key])
        return cls(**dict_)
    

@dataclass(frozen=True)
class Paths:
    dir_: Path
    metadata_file_name:str = "metadata.json"
    recon_file_name:FunctionType = lambda subtrial: f"recon_{subtrial}.root"
    sim_file_name:FunctionType = lambda subtrial: f"sim_{subtrial}.root"
    decay_file_name:str = "decay.dec"
    log_file_name:str = "log.log"

    @cached_property
    def metadata_file_path(
        self,
    ) -> Path:
        return self.dir_.joinpath(self.metadata_file_name)
    
    def recon_file_path(
        self, 
        subtrial:int
    ) -> Path:
        recon_file_name = self.recon_file_name(subtrial)
        return self.dir_.joinpath(recon_file_name)
    
    def sim_file_path(
        self, 
        subtrial:int,
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
    
