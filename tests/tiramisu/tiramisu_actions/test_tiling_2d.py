from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.tiling_2d import Tiling2D
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_tiling_2d_init():
    tiling_2d = Tiling2D(["i0", "i1", 32, 32], ["comp00"])
    assert tiling_2d.params == ["i0", "i1", 32, 32]
    assert tiling_2d.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.tiling_2d_sample()
    tiling_2d = Tiling2D(["i0", "i1", 32, 32], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimization(tiling_2d)
    assert tiling_2d.tiramisu_optim_str == "\n\tcomp00.tile(0, 1, 32, 32);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.tiling_2d_sample()
    candidates = Tiling2D.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1")]}

    candidates = Tiling2D.get_candidates(test_utils.tree_test_sample())
    assert candidates == {"root": [("j", "k")]}
