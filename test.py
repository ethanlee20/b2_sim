
from dataclasses import dataclass, fields, asdict, is_dataclass
from copy import deepcopy


def read_nested_dict(dict_, keys: list):
    for key in keys:
        dict_ = dict_[key]
    return dict_


def write_nested_dict(dict_, keys:list, value):
    dict_ = read_nested_dict(dict_, keys[:-1])
    dict_[keys[-1]] = value


def _rebuild(cls, dict_, keys:list|None=None):
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


def rebuild(cls, dict_):
    dict_ = deepcopy(dict_)
    out = _rebuild(cls, dict_)
    return out


@dataclass
class C:
    c: int
    c_: int


@dataclass
class B:
    b: C
    b_: C


@dataclass
class A:
    a: B
    a_: B


if __name__ == "__main__":

    a = A(B(C(1,2),C(3,4)), B(C(5,6),C(7,8)))

    a_dict = asdict(a)

    print(a)
    print(a_dict)
    
    
    a_rebuild = rebuild(A, a_dict)

    print(a)
    print(a_dict)

    print(a == a_rebuild)