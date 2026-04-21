
from dataclasses import astuple
from pathlib import Path
from random import seed, uniform
from itertools import product

from .util import (
    Delta_WC_Values, 
    Delta_WC_Counts,
    Delta_WC_Intervals, 
    Metadata, 
    Paths, 
    linspace,
)


class Random_Sampler:
    def __init__(
        self, 
        delta_wc_intervals:Delta_WC_Intervals,
        seed_:int|None=None,
    ):
        seed(seed_)
        self.delta_wc_intervals = delta_wc_intervals

    def sample(
        self, 
        n:int,
    ) -> list[Delta_WC_Values]:
        return [
            self._sample()
            for _ in range(n)
        ]
    
    def _sample(
        self,
    ) -> Delta_WC_Values:
        return Delta_WC_Values(
            *(
                uniform(*interval) 
                for interval in self.delta_wc_intervals
            )
        )


class Grid_Sampler:
    def __init__(
        self,
        delta_wc_intervals:Delta_WC_Intervals,
    ):
        self.delta_wc_intervals = delta_wc_intervals

    def make_grid(
        self, 
        n:Delta_WC_Counts,
    ):
        samples = self.sample_per_wc(n)
        grid = product(*samples)
        grid = [Delta_WC_Values(*i) for i in grid]
        return grid

    def sample_per_wc(
        self,
        n:Delta_WC_Counts,
    ) -> list[list[float]]:
        samples = []
        for interval, count in zip(
            self.delta_wc_intervals, 
            n,
        ):
            samples.append(
                linspace(
                    interval=interval, 
                    num_points=count
                )
            )
        return samples


def _make_metadatas(
    delta_wc_samples:list[Delta_WC_Values],
    num_events_per_trial:int,
    num_subtrials_per_trial:int,
    split:str,
    lepton_flavor:str,
    delta_wc_intervals:Delta_WC_Intervals,
) -> list[Metadata]:
    return [
        Metadata(
            trial, 
            num_events_per_trial, 
            num_subtrials_per_trial,
            split,
            lepton_flavor,
            sample,
            delta_wc_intervals,
        ) for trial, sample in enumerate( 
            delta_wc_samples
        )
    ]


def _make_trial_dir_name(
    metadata:Metadata,
) -> str:
    name = (
        f"{metadata.trial_num}"
        f"_{metadata.split}"
        f"_{metadata.num_events}"
        f"_{metadata.lepton_flavor}"
    )
    for wc in astuple(metadata.delta_wc_values):
        name += f"_{wc:.2f}"
    return name


def _setup_trial_dirs(
    dir_:Path,
    metadatas:list[Metadata],
) -> None:
    if not dir_.is_dir():
        raise ValueError(
            "Data directory is not a directory."
            f" ({dir_})"
        )
    dir_paths = [
        dir_.joinpath(_make_trial_dir_name(m)) 
        for m in metadatas
    ]
    for p, m in zip(
        dir_paths, 
        metadatas,
    ):
        p.mkdir()
        m.to_json_file(
            Paths(p).metadata_file_path
        )


def setup_dir(
    dir_:Path,  
    delta_wc_samples:list[Delta_WC_Values],
    num_events_per_trial:int,
    num_subtrials_per_trial:int,
    split:str,
    lepton_flavor:str,
    delta_wc_intervals:Delta_WC_Intervals,
) -> None:
    dir_.mkdir(
        parents=True,
        exist_ok=False
    )
    metadatas = _make_metadatas(
        delta_wc_samples, 
        num_events_per_trial, 
        num_subtrials_per_trial, 
        split, 
        lepton_flavor, 
        delta_wc_intervals,
    )
    _setup_trial_dirs(
        dir_,
        metadatas,
    )