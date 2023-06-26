from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.unrolling import Unrolling
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_reversal_init():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    reversal = Unrolling(["i0", 4], sample.tree)
    assert reversal.params == ["i0", 4]
    assert reversal.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    reversal = Unrolling(["i0", 4], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([reversal])
    assert reversal.tiramisu_optim_str == "comp00.unroll(0,4);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    candidates = Unrolling.get_candidates(sample.tree)
    assert candidates == ["i1"]

    candidates = Unrolling.get_candidates(test_utils.tree_test_sample())
    assert candidates == ["i", "l", "m"]


def test_legality_check_string():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()
    unrolling = Unrolling(["i0", 4], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([unrolling])

    assert schedule.tree
    assert (
        unrolling.legality_check_string(schedule.tree)
        == "is_legal &= loop_unrolling_is_legal(0, {&comp00});\n    comp00.unroll(0,4);\n"
    )


def test_transform_tree():
    BaseConfig.init()
    sample = test_utils.unrolling_sample()

    Unrolling(["i0", 4], sample.tree).transform_tree(sample.tree)

    assert sample.tree.iterators["i0"].upper_bound == 192
    assert sample.tree.iterators["i0"].lower_bound == 0
    assert sample.tree.iterators["i0"].child_iterators == ["i0_unroll"]
    assert sample.tree.iterators["i0_unroll"].lower_bound == 0
    assert sample.tree.iterators["i0_unroll"].upper_bound == 4
    assert sample.tree.iterators["i0_unroll"].parent_iterator == "i0"
    assert sample.tree.iterators["i0_unroll"].child_iterators == ["i1"]

    sample = test_utils.unrolling_sample()

    Unrolling(["i0", 400], sample.tree).transform_tree(sample.tree)

    assert sample.tree.iterators["i0"].upper_bound == 400
    assert sample.tree.iterators["i0"].lower_bound == 0
    assert sample.tree.iterators["i0"].child_iterators == ["i1"]

    assert sample.tree.roots == ["i0", "i0_unroll"]
    assert sample.tree.iterators["i0_unroll"].lower_bound == 400
    assert sample.tree.iterators["i0_unroll"].upper_bound == 768
    assert sample.tree.iterators["i0_unroll"].child_iterators == ["i1_unroll"]
    assert sample.tree.iterators["i1_unroll"].parent_iterator == "i0_unroll"
    assert sample.tree.iterators["i1_unroll"].lower_bound == 0
    assert sample.tree.iterators["i1_unroll"].upper_bound == 16
    assert sample.tree.iterators["i1_unroll"].computations_list == ["comp00_unroll"]
    assert sample.tree.computations == ["comp00", "comp00_unroll"]

    sample = test_utils.unrolling_sample()

    Unrolling(["i0", 155], sample.tree).transform_tree(sample.tree)

    assert sample.tree.iterators["i0"].lower_bound == 0
    assert sample.tree.iterators["i0"].upper_bound == 4
    assert sample.tree.iterators["i0"].child_iterators == ["i0_child_unroll"]
    assert sample.tree.iterators["i0_child_unroll"].lower_bound == 0
    assert sample.tree.iterators["i0_child_unroll"].upper_bound == 155
    assert sample.tree.iterators["i0_child_unroll"].parent_iterator == "i0"
    assert sample.tree.iterators["i0_child_unroll"].child_iterators == ["i1"]
    assert sample.tree.iterators["i1"].parent_iterator == "i0_child_unroll"

    assert sample.tree.roots == ["i0", "i0_unroll"]
    assert sample.tree.iterators["i0_unroll"].lower_bound == 620
    assert sample.tree.iterators["i0_unroll"].upper_bound == 768
    assert sample.tree.iterators["i0_unroll"].child_iterators == ["i1_unroll"]
    assert sample.tree.iterators["i1_unroll"].parent_iterator == "i0_unroll"
    assert sample.tree.iterators["i1_unroll"].lower_bound == 0
    assert sample.tree.iterators["i1_unroll"].upper_bound == 16
    assert sample.tree.iterators["i1_unroll"].computations_list == ["comp00_unroll"]
    assert sample.tree.computations == ["comp00", "comp00_unroll"]
