from dataclasses import dataclass, astuple, make_dataclass
from copy import deepcopy


@dataclass 
class ParameterBase:
    def __iter__(self):
        tuple_ = astuple(self)
        out = tuple_.__iter__()
        return out


def make_parameter_dataclass(name:str, type_:Any, *args: str) -> type[Any]:
    out = make_dataclass(
        name,
        [(arg, type_) for arg in args],
        bases=(ParameterBase,)
    )
    return out


@dataclass
class ParameterCounts:
    @classmethod
    def make(cls, *args):
        out = make_parameter_dataclass(cls.__name__, int, *args)
        return out