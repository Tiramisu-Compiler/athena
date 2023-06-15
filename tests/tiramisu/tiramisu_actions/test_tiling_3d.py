from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.tiling_3d import Tiling3D
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_tiling_3d_init():
    tiling_2d = Tiling3D(["i0", "i1", "i2", 32, 32, 32], ["comp00"])
    assert tiling_2d.params == ["i0", "i1", "i2", 32, 32, 32]
    assert tiling_2d.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.tiling_3d_sample()
    tiling_3d = Tiling3D(["i0", "i1", "i2", 32, 32, 32], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimizations([tiling_3d])
    assert tiling_3d.tiramisu_optim_str == "\n\tcomp00.tile(0, 1, 2, 32, 32, 32);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.tiling_3d_sample()
    candidates = Tiling3D.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1", "i2")]}

    candidates = Tiling3D.get_candidates(test_utils.tiling_3d_tree_sample())
    assert candidates == {"root": [("root", "j", "k"), ("j", "k", "l")]}
