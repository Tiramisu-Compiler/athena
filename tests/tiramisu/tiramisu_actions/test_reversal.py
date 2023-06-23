from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.reversal import Reversal
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_reversal_init():
    reversal = Reversal(["i0"], ["comp00"])
    assert reversal.params == ["i0"]
    assert reversal.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    reversal = Reversal(["i0"], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimizations([reversal])
    assert reversal.tiramisu_optim_str == "comp00.loop_reversal(0);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    candidates = Reversal.get_candidates(sample.tree)
    assert candidates == {"i0": ["i0", "i1"]}


def test_transform_tree():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    iterator = sample.tree.get_iterator_node("i0")
    lower, upper = iterator.lower_bound, iterator.upper_bound
    reversal = Reversal(["i0"], ["comp00"])
    reversal.transform_tree(sample.tree)
    assert iterator.lower_bound == upper and iterator.upper_bound == lower
