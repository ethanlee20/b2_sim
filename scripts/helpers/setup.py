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
class RandomSampler:
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
class GridSampler:
    bounds: DeltaWCBounds

    def sample(
        self,
        n: DeltaWCCounts
    ) -> list[DeltaWCValues]:
        samples_per_wc = self._samples_per_wc(n)
        out = product(*samples_per_wc)
        out = [DeltaWCValues(*vals) for vals in grid]
        return out

    def _samples_per_wc(
        self,
        n: DeltaWCCounts,
    ) -> list[list[float, ...], ...]:
        out = [linspace(*b, n_) for b, n_ in zip(self.bounds, n)]
        return out


def run_dir_name(split: str) -> str:
    out = f"{split}"
    return out


def trial_dir_name(trial_num: int) -> str:
    out = f"{trial_num}"
    return out


def run_dir_path(split:str, parent_dir_path:Path) -> Path:
    name = run_dir_name(split)
    out = parent_dir_path.joinpath(name)
    return out


def trial_dir_path(trial_num: int, parent_dir_path: Path) -> Path:
    name = trial_dir_name(trial_num)
    out = parent_dir_path.joinpath(name)
    return out


def setup_trial_dir(trial_metadata: TrialMetadata, parent_dir_path:Path) -> None:
    trial_num = trial_metadata.trial_num
    dir_ = trial_dir_path(trial_num, parent_dir_path)
    dir_.mkdir()
    save_metadata_to_dir(trial_metadata, dir_,)


def setup_run_dir(run_metadata: RunMetadata, delta_wc_values_list:list[DeltaWCValues], parent_dir_path:Path) -> None:
    split = run_metadata.split
    dir_ = run_dir_path(split, parent_dir_path)
    dir_.mkdir()
    save_metadata_to_dir(run_metadata, dir_,)
    trial_metadatas = make_trial_metadata_list(run_metadata, delta_wc_values_list)
    for trial_metadata in trial_metadatas:
        setup_trial_dir(trial_metadata, dir_)