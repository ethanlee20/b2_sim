from typing import Any
from itertools import product
from dataclasses import dataclass, asdict, fields, is_dataclass
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
