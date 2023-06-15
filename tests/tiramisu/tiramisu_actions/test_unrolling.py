from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.unrolling import Unrolling
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_reversal_init():
    reversal = Unrolling(["i0", 4], ["comp00"])
    assert reversal.params == ["i0", 4]
    assert reversal.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    reversal = Unrolling(["i0", 4], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimizations([reversal])
    assert reversal.tiramisu_optim_str == "\n\tcomp00.unroll(0,4);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    candidates = Unrolling.get_candidates(sample.tree)
    assert candidates == ["i1"]

    candidates = Unrolling.get_candidates(test_utils.tree_test_sample())
    assert candidates == ["i", "l", "m"]
