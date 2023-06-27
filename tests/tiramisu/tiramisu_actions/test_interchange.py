import pytest
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.tiramisu.tiramisu_actions.tiling_2d import Tiling2D
from athena.tiramisu.tiramisu_actions.tiramisu_action import CannotApplyException
from athena.utils.config import BaseConfig
from tests.utils import interchange_example
import tests.utils as test_utils


def test_interchange_init():
    BaseConfig.init()
    sample = interchange_example()
    interchange = Interchange(["i0", "i1"], sample.tree)
    assert interchange.params == ["i0", "i1"]
    assert interchange.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = interchange_example()
    interchange = Interchange(["i0", "i1"], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([interchange])
    assert interchange.tiramisu_optim_str == "comp00.interchange(0,1);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = interchange_example()
    candidates = Interchange.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1"), ("i0", "i2"), ("i1", "i2")]}


def test_transform_tree():
    t_tree = test_utils.tree_test_sample()
    interchange = Interchange(["i", "j"], t_tree)

    interchange.transform_tree(t_tree)

    assert t_tree.iterators["i"].parent_iterator == "root"
    assert t_tree.iterators["j"].parent_iterator == "root"

    assert t_tree.iterators["i"].child_iterators == ["k"]
    assert not t_tree.iterators["j"].child_iterators

    assert t_tree.iterators["k"].parent_iterator == "i"
    assert t_tree.iterators["j"].computations_list == ["comp01"]

    t_tree = test_utils.tree_test_sample()

    Interchange(["j", "k"], t_tree).transform_tree(t_tree)

    assert t_tree.iterators["k"].parent_iterator == "root"
    assert t_tree.iterators["k"].child_iterators == ["j"]

    assert t_tree.iterators["j"].parent_iterator == "k"
    assert t_tree.iterators["j"].child_iterators == ["l", "m"]

    assert t_tree.iterators["l"].parent_iterator == "j"
    assert t_tree.iterators["m"].parent_iterator == "j"

    t_tree = test_utils.tree_test_sample()

    Interchange(["root", "j"], t_tree).transform_tree(t_tree)

    assert t_tree.roots == ["j"]
    assert t_tree.iterators["j"].parent_iterator == None
    assert t_tree.iterators["j"].child_iterators == ["i", "root"]

    assert t_tree.iterators["root"].parent_iterator == "j"
    assert t_tree.iterators["root"].child_iterators == ["k"]

    assert t_tree.iterators["k"].parent_iterator == "root"


def test_verify_conditions():
    BaseConfig.init()

    sample = test_utils.multiple_roots_sample()

    interchange = Interchange(["i", "j"], sample.tree)

    interchange.verify_conditions(sample.tree)

    schedule = Schedule(sample)
    schedule.add_optimizations([Tiling2D(["i", "j", 7, 10], schedule.tree)])

    assert schedule.tree

    with pytest.raises(CannotApplyException) as e_info:
        Interchange(["i_tiled", "j_tile"], schedule.tree).verify_conditions(
            schedule.tree
        )

    assert "Cannot interchange i_tiled and j_tile because" in str(e_info.value)
