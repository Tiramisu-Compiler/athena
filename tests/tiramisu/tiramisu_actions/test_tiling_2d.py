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
    schedule.add_optimizations([tiling_2d])
    assert tiling_2d.tiramisu_optim_str == "comp00.tile(0, 1, 32, 32);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.tiling_2d_sample()
    candidates = Tiling2D.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1")]}

    candidates = Tiling2D.get_candidates(test_utils.tree_test_sample())
    assert candidates == {"root": [("j", "k")]}


def test_transform_tree():
    BaseConfig.init()
    sample = test_utils.tiling_2d_sample()

    tiling_2d = Tiling2D(["i0", "i1", 32, 32], ["comp00"])
    tiling_2d.transform_tree(sample.tree)

    assert sample.tree.get_iterator_node("i0").lower_bound == 0
    assert sample.tree.get_iterator_node("i0").upper_bound == 2
    assert sample.tree.get_iterator_node("i0").child_iterators == ["i1"]
    assert not sample.tree.get_iterator_node("i0").computations_list
    assert sample.tree.get_iterator_node("i0").level == 0

    assert sample.tree.get_iterator_node("i1").lower_bound == 0
    assert sample.tree.get_iterator_node("i1").upper_bound == 6
    assert sample.tree.get_iterator_node("i1").child_iterators == ["i0_tiled"]
    assert not sample.tree.get_iterator_node("i1").computations_list
    assert sample.tree.get_iterator_node("i1").level == 1

    assert sample.tree.get_iterator_node("i0_tiled").lower_bound == 0
    assert sample.tree.get_iterator_node("i0_tiled").upper_bound == 32
    assert sample.tree.get_iterator_node("i0_tiled").child_iterators == ["i1_tiled"]
    assert not sample.tree.get_iterator_node("i0_tiled").computations_list
    assert sample.tree.get_iterator_node("i0_tiled").parent_iterator == "i1"
    assert sample.tree.get_iterator_node("i0_tiled").level == 2

    assert sample.tree.get_iterator_node("i1_tiled").lower_bound == 0
    assert sample.tree.get_iterator_node("i1_tiled").upper_bound == 32
    assert not sample.tree.get_iterator_node("i1_tiled").child_iterators
    assert sample.tree.get_iterator_node("i1_tiled").computations_list == ["comp00"]
    assert sample.tree.get_iterator_node("i1_tiled").parent_iterator == "i0_tiled"
    assert sample.tree.get_iterator_node("i1_tiled").level == 3

    sample = test_utils.benchmark_program_test_sample()

    tiling_2d = Tiling2D(["i00", "i01", 32, 11], ["comp02"])

    tiling_2d.transform_tree(sample.tree)

    assert sample.tree.get_iterator_node("i00").lower_bound == 0
    assert sample.tree.get_iterator_node("i00").upper_bound == 6
    assert sample.tree.get_iterator_node("i00").child_iterators == ["i01"]
    assert not sample.tree.get_iterator_node("i00").computations_list
    assert sample.tree.get_iterator_node("i00").level == 0

    assert sample.tree.get_iterator_node("i01").lower_bound == 0
    assert sample.tree.get_iterator_node("i01").upper_bound == 24
    assert sample.tree.get_iterator_node("i01").child_iterators == ["i00_tiled"]
    assert not sample.tree.get_iterator_node("i01").computations_list
    assert sample.tree.get_iterator_node("i01").level == 1

    assert sample.tree.get_iterator_node("i00_tiled").lower_bound == 0
    assert sample.tree.get_iterator_node("i00_tiled").upper_bound == 32
    assert sample.tree.get_iterator_node("i00_tiled").child_iterators == ["i01_tiled"]
    assert not sample.tree.get_iterator_node("i00_tiled").computations_list
    assert sample.tree.get_iterator_node("i00_tiled").parent_iterator == "i01"
    assert sample.tree.get_iterator_node("i00_tiled").level == 2

    assert sample.tree.get_iterator_node("i01_tiled").lower_bound == 0
    assert (
        sample.tree.get_iterator_node("i01_tiled").upper_bound
        == "(256 - max(i01*11, 245))"
    )
    assert sample.tree.get_iterator_node("i01_tiled").child_iterators == ["i02"]
    assert not sample.tree.get_iterator_node("i01_tiled").computations_list
    assert sample.tree.get_iterator_node("i01_tiled").parent_iterator == "i00_tiled"
    assert sample.tree.get_iterator_node("i01_tiled").level == 3

    assert sample.tree.get_iterator_node("i02").lower_bound == 0
    assert sample.tree.get_iterator_node("i02").upper_bound == 320
    assert not sample.tree.get_iterator_node("i02").child_iterators
    assert sample.tree.get_iterator_node("i02").computations_list == ["comp02"]
    assert sample.tree.get_iterator_node("i02").parent_iterator == "i01_tiled"
    assert sample.tree.get_iterator_node("i02").level == 4
