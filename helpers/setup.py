from pathlib import Path
from random import seed, uniform
from itertools import product

from .util import (
    ParameterValues,
    ParameterCounts,
    ParameterIntervals,
    TrialMetadata,
    FilePaths,
    linspace,
)


def set_random_seed(seed_: int | None = None):
    seed(seed_)


@dataclass
class RandomSampler:
    parameter_bounds: ParameterBounds

    def sample(
        self,
        n: int,
    ) -> list[ParameterValues]:
        out = [self._sample_once() for _ in range(n)]
        return out

    def _sample_once(
        self,
    ) -> ParameterValues:
        names = self.parameter_bounds.names
        values = (uniform(*b) for b in self.parameter_bounds.bounds)
        out = ParameterValues(names=names, values=values)
        return out


@dataclass
class GridSampler:
    parameter_bounds: ParameterBounds

    def sample(self, parameter_counts: ParameterCounts) -> list[ParameterValues]:
        samples_per_wc = self._samples_per_wc(n)
        samples = product(*samples_per_wc)
        names = self.parameter_bounds.names
        out = [ParameterValues(names=names, values=sample) for sample in samples]
        return out

    def _samples_per_wc(
        self,
        parameter_counts: ParameterCounts,
    ) -> list[list[float, ...], ...]:
        assert parameter_counts.names == self.parameter_bounds.names
        out = [
            linspace(*bounds, count)
            for bounds, count in zip(self.parameter_bounds, parameter_counts.counts)
        ]
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
    parameter_values_list: list[ParameterValues],
    parent_dir_path: Path | str,
) -> None:
    split = run_metadata.split
    dir_ = run_dir_path(split, parent_dir_path)
    dir_.mkdir()
    save_metadata_to_dir(
        run_metadata,
        dir_,
    )
    trial_metadatas = make_trial_metadata_list(run_metadata, parameter_values_list)
    for trial_metadata in trial_metadatas:
        setup_trial_dir(trial_metadata, dir_)
    return dir_
