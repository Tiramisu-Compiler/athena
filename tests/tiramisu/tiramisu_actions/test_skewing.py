from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.skewing import Skewing
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_skewing_init():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    skewing = Skewing(["i0", "i1", 5, 5], sample.tree)
    assert skewing.params == ["i0", "i1", 5, 5]
    assert skewing.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    skewing = Skewing(["i0", "i1", 1, 1], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([skewing])
    assert skewing.tiramisu_optim_str == "comp00.skew(0, 1, 1, 1);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    candidates = Skewing.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1"), ("i1", "i2")]}

    candidates = Skewing.get_candidates(test_utils.tree_test_sample())
    assert candidates == {"root": [("j", "k")]}


def test_get_factors():
    BaseConfig.init()
    sample = test_utils.skewing_example()
    loop_levels = sample.tree.get_iterator_levels(["i0", "i1"])
    schedule = Schedule(sample)
    factors = Skewing.get_factors(
        schedule=schedule,
        loop_levels=loop_levels,
        comps_skewed_loops=sample.tree.get_iterator_subtree_computations("i0"),
    )
    assert factors == (1, 1)


def test_transform_tree():
    BaseConfig.init()

    sample = test_utils.multiple_roots_sample()

    Skewing(["i_0", "j_0", 1, 1], sample.tree).transform_tree(sample.tree)

    assert sample.tree.get_iterator_node("i_0").lower_bound == "UNK"
    assert sample.tree.get_iterator_node("i_0").upper_bound == "UNK"
    assert sample.tree.get_iterator_node("j_0").lower_bound == "UNK"
    assert sample.tree.get_iterator_node("j_0").upper_bound == "UNK"
