from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.tiling_3d import Tiling3D
from athena.utils.config import BaseConfig
import tests.utils as test_utils
import pytest


def test_tiling_3d_init():
    BaseConfig.init()
    sample = test_utils.tiling_3d_sample()
    tiling_2d = Tiling3D(["i0", "i1", "i2", 32, 32, 32], sample.tree)
    assert tiling_2d.params == ["i0", "i1", "i2", 32, 32, 32]
    assert tiling_2d.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.tiling_3d_sample()
    tiling_3d = Tiling3D(["i0", "i1", "i2", 32, 32, 32], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([tiling_3d])
    assert tiling_3d.tiramisu_optim_str == "comp00.tile(0, 1, 2, 32, 32, 32);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.tiling_3d_sample()
    candidates = Tiling3D.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1", "i2")]}

    candidates = Tiling3D.get_candidates(test_utils.tiling_3d_tree_sample())
    assert candidates == {"root": [("root", "j", "k"), ("j", "k", "l")]}


def test_transform_tree():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()

    Tiling3D(["i00", "i01", "i02", 32, 32, 32], sample.tree).transform_tree(sample.tree)

    assert sample.tree.iterators["i00"].parent_iterator == None
    assert sample.tree.iterators["i00"].child_iterators == ["i01"]
    assert sample.tree.iterators["i00"].lower_bound == 0
    assert sample.tree.iterators["i00"].upper_bound == 6
    assert sample.tree.iterators["i00"].level == 0

    assert sample.tree.iterators["i01"].parent_iterator == "i00"
    assert sample.tree.iterators["i01"].child_iterators == ["i02"]
    assert sample.tree.iterators["i01"].lower_bound == 0
    assert sample.tree.iterators["i01"].upper_bound == 8
    assert sample.tree.iterators["i01"].level == 1

    assert sample.tree.iterators["i02"].parent_iterator == "i01"
    assert sample.tree.iterators["i02"].child_iterators == ["i00_tiled"]
    assert sample.tree.iterators["i02"].lower_bound == 0
    assert sample.tree.iterators["i02"].upper_bound == 10
    assert not sample.tree.iterators["i02"].computations_list
    assert sample.tree.iterators["i02"].level == 2

    assert sample.tree.iterators["i00_tiled"].parent_iterator == "i02"
    assert sample.tree.iterators["i00_tiled"].child_iterators == ["i01_tiled"]
    assert sample.tree.iterators["i00_tiled"].lower_bound == 0
    assert sample.tree.iterators["i00_tiled"].upper_bound == 32
    assert not sample.tree.iterators["i00_tiled"].computations_list
    assert sample.tree.iterators["i00_tiled"].level == 3

    assert sample.tree.iterators["i01_tiled"].parent_iterator == "i00_tiled"
    assert sample.tree.iterators["i01_tiled"].child_iterators == ["i02_tiled"]
    assert sample.tree.iterators["i01_tiled"].lower_bound == 0
    assert sample.tree.iterators["i01_tiled"].upper_bound == 32
    assert not sample.tree.iterators["i01_tiled"].computations_list
    assert sample.tree.iterators["i01_tiled"].level == 4

    assert sample.tree.iterators["i02_tiled"].parent_iterator == "i01_tiled"
    assert sample.tree.iterators["i02_tiled"].child_iterators == []
    assert sample.tree.iterators["i02_tiled"].lower_bound == 0
    assert sample.tree.iterators["i02_tiled"].upper_bound == 32
    assert sample.tree.iterators["i02_tiled"].computations_list == ["comp02"]
    assert sample.tree.iterators["i02_tiled"].level == 5


def test_verify_conditions():
    BaseConfig.init()

    t_tree = test_utils.tree_test_sample()

    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "k", "l", 256, 32, 32], t_tree).verify_conditions(t_tree)
    assert "are not successive" in str(e.value)

    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "l", 32, 32, 32], t_tree).verify_conditions(t_tree)
    assert "are not successive" in str(e.value)

    t_tree.iterators["j"].lower_bound = ""
    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, 32, 32], t_tree).verify_conditions(t_tree)
    assert "has non-integer bounds" in str(e.value)
    t_tree.iterators["j"].lower_bound = 0

    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, -2, 32], t_tree).verify_conditions(t_tree)
    assert "must be positive" in str(e.value)

    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, 32, 512], t_tree).verify_conditions(t_tree)
    assert "must be smaller" in str(e.value)

    t_tree.iterators["root"].computations_list = ["comp00"]
    t_tree.computations_absolute_order = {
        "comp00": 1,
        "comp01": 2,
        "comp03": 3,
        "comp04": 4,
    }
    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, 32, 5], t_tree).verify_conditions(t_tree)
    assert "The first node must not have any computations" in str(e.value)
    t_tree = test_utils.tree_test_sample()

    t_tree.iterators["j"].computations_list = ["comp00"]
    t_tree.computations_absolute_order = {
        "comp01": 1,
        "comp00": 2,
        "comp03": 3,
        "comp04": 4,
    }
    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, 32, 5], t_tree).verify_conditions(t_tree)
    assert "The second node must not have any computations" in str(e.value)

    t_tree = test_utils.tree_test_sample()

    with pytest.raises(AssertionError) as e:
        Tiling3D(["root", "j", "k", 32, 32, 5], t_tree).verify_conditions(t_tree)
    assert "The first node must have one child" in str(e.value)

    with pytest.raises(AssertionError) as e:
        Tiling3D(["j", "k", "l", 32, 5, 5], t_tree).verify_conditions(t_tree)
    assert "The second node must have one child" in str(e.value)

    t_tree.iterators["k"].child_iterators = ["l"]
    Tiling3D(["j", "k", "l", 32, 5, 8], t_tree).verify_conditions(t_tree)
