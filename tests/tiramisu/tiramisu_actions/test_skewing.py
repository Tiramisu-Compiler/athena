from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.skewing import Skewing
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_skewing_init():
    skewing = Skewing(["i0", "i1", 5, 5], ["comp00"])
    assert skewing.params == ["i0", "i1", 5, 5]
    assert skewing.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    skewing = Skewing(["i0", "i1", 1, 1], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimization(skewing)
    assert skewing.tiramisu_optim_str == "comp00.skew(0, 1, 1, 1);\n\t"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    candidates = Skewing.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1"), ("i1", "i2")]}


def test_get_factors():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    factors = Skewing.get_factors(
        loops=["i0", "i1"], current_schedule=[], tiramisu_program=sample
    )
    assert factors == (1, 1)
