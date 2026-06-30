from itertools import product

a = {"b": [1, 2, 3], "c": [4, 5, 6]}
prod = product(*a.values())
rrr = [dict(zip(a.keys(), i)) for i in prod]

breakpoint()
