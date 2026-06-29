from dataclasses import dataclass

from test2 import ParameterCounts


if __name__ == "__main__":


    @dataclass
    class Meta:
        p: ParameterCounts


    p_counts = ParameterCounts.make("dc9", "dc10", "dc7")(1, 2, 3)
    m = Meta(p_counts)
    
    breakpoint()