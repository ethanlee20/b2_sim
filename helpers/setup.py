from pathlib import Path
from random import seed, uniform
from dataclasses import dataclass

from .util import (
    product_combine,
    Interval,
    linspace,
    TrialMetadata,
    RunMetadata,
    save_metadata_to_dir,
    make_trial_metadata_list,
)


def set_random_seed(seed_: int | None = None):
    seed(seed_)


@dataclass
class RandomSampler:
    parameter_bounds: dict[str, Interval]

    def sample(
        self,
        n: int,
    ) -> list[dict[str, float]]:
        out = [self._sample_once() for _ in range(n)]
        return out

    def _sample_once(
        self,
    ) -> dict[str, float]:
        out = {name: uniform(*bounds) for name, bounds in self.parameter_bounds.items()}
        return out


@dataclass
class GridSampler:
    parameter_bounds: dict[str, Interval]

    def sample(self, parameter_counts: dict[str, int]) -> list[dict[str, float]]:
        samples_per_wc = self._samples_per_wc(parameter_counts)
        out = product_combine(samples_per_wc)
        return out

    def _samples_per_wc(
        self,
        parameter_counts: dict[str, int],
    ) -> dict[str, list[float]]:
        assert parameter_counts.keys() == self.parameter_bounds.keys()
        out = {
            name: linspace(*self.parameter_bounds[name], count)
            for name, count in parameter_counts.items()
        }
        return out


def run_dir_name(split: str) -> str:
    out = f"{split}"
    return out


def trial_dir_name(trial_num: int) -> str:
    out = f"{trial_num}"
    return out


def run_dir_path(split: str, parent_dir_path: Path | str) -> Path:
    parent_dir_path = Path(parent_dir_path)
    name = run_dir_name(split)
    out = parent_dir_path.joinpath(name)
    return out


def trial_dir_path(trial_num: int, parent_dir_path: Path | str) -> Path:
    parent_dir_path = Path(parent_dir_path)
    name = trial_dir_name(trial_num)
    out = parent_dir_path.joinpath(name)
    return out


def setup_trial_dir(trial_metadata: TrialMetadata, parent_dir_path: Path | str) -> None:
    trial_num = trial_metadata.trial_num
    dir_ = trial_dir_path(trial_num, parent_dir_path)
    dir_.mkdir()
    save_metadata_to_dir(
        trial_metadata,
        dir_,
    )


def setup_run_dir(
    run_metadata: RunMetadata,
    parameter_values: list[dict[str, float]],
    parent_dir_path: Path | str,
) -> None:
    split = run_metadata.split
    dir_ = run_dir_path(split, parent_dir_path)
    dir_.mkdir(parents=True)
    save_metadata_to_dir(
        run_metadata,
        dir_,
    )
    trial_metadatas = make_trial_metadata_list(run_metadata, parameter_values)
    for trial_metadata in trial_metadatas:
        setup_trial_dir(trial_metadata, dir_)
    return dir_
