import tests.utils as test_utils
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.reversal import Reversal
from athena.utils.config import BaseConfig


def test_reversal_init():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    reversal = Reversal(("comp00", 0), sample.tree)
    assert reversal.iterator.name == "i0"
    assert reversal.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    reversal = Reversal(("comp00", 0), sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([reversal])
    assert reversal.tiramisu_optim_str == "comp00.loop_reversal(0);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.reversal_sample()
    candidates = Reversal.get_candidates(sample.tree)
    assert candidates == {"i0": ["i0", "i1"]}
