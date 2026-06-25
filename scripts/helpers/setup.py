from dataclasses import astuple
from pathlib import Path
from random import seed, uniform
from itertools import product

from .util import (
    Delta_WC_Values,
    Delta_WC_Counts,
    Delta_WC_Intervals,
    Trial_Metadata,
    Paths,
    linspace,
)


def set_random_seed(seed_: int | None = None):
    seed(seed_)


@dataclass
class Random_Sampler:
    bounds: DeltaWCBounds

    def sample(
        self,
        n: int,
    ) -> list[DeltaWCValues]:
        out = [self._sample_once() for _ in range(n)]
        return out

    def _sample_once(
        self,
    ) -> DeltaWCValues:
        out = uniform(*b) for b in self.bounds
        return out
        

@dataclass
class Grid_Sampler:
    bounds: DeltaWCBounds

    def sample(
        self,
        counts: DeltaWCCounts
    ):
        samples = self._sample_per_wc(n)
        grid = product(*samples)
        grid = [Delta_WC_Values(*i) for i in grid]
        return grid

    def _sample_per_wc(
        self,
        n: Delta_WC_Counts,
    ) -> list[tuple[float, ...]]:
        samples = []
        for interval, count in zip(
            self.delta_wc_intervals,
            n,
        ):
            samples.append(linspace(interval=interval, num_points=count))
        return samples

    def _sample(self, n:int, ) -> tuple[float, ...]:
        linspace() 


def _make_metadatas(
    delta_wc_samples: list[Delta_WC_Values],
    num_events_per_trial: int,
    num_subtrials_per_trial: int,
    split: str,
    lepton_flavor: str,
    delta_wc_intervals: Delta_WC_Intervals,
) -> list[Trial_Metadata]:
    return [
        Trial_Metadata(
            trial,
            num_events_per_trial,
            num_subtrials_per_trial,
            split,
            lepton_flavor,
            sample,
            delta_wc_intervals,
        )
        for trial, sample in enumerate(delta_wc_samples)
    ]


def _make_trial_dir_name(
    metadata: Trial_Metadata,
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
    dir_: Path,
    metadatas: list[Trial_Metadata],
) -> None:
    if not dir_.is_dir():
        raise ValueError("Data directory is not a directory." f" ({dir_})")
    dir_paths = [dir_.joinpath(_make_trial_dir_name(m)) for m in metadatas]
    for p, m in zip(
        dir_paths,
        metadatas,
    ):
        p.mkdir()
        m.to_json_file(Paths(p).metadata_file_path)


def setup_dir(
    dir_: Path,
    delta_wc_samples: list[Delta_WC_Values],
    num_events_per_trial: int,
    num_subtrials_per_trial: int,
    split: str,
    lepton_flavor: str,
    delta_wc_intervals: Delta_WC_Intervals,
) -> None:
    dir_.mkdir(parents=True, exist_ok=False)
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
