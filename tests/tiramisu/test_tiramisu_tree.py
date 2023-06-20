from athena.utils.config import BaseConfig
import tests.utils as test_utils
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree


def test_from_annotations():
    data, _ = test_utils.load_test_data()
    # get program of first key from data
    program = data[list(data.keys())[0]]
    tiramisu_tree = TiramisuTree.from_annotations(program["program_annotation"])
    assert len(tiramisu_tree.roots) == 1

    BaseConfig.init()
    multi_roots = test_utils.multiple_roots_sample().tree

    assert len(multi_roots.roots) == 4
    assert len(multi_roots.iterators) == 7
    assert len(multi_roots.computations) == 4

    assert multi_roots.computations_absolute_order == {
        "A_hat": 1,
        "x_temp": 2,
        "x": 3,
        "w": 4,
    }


def test_get_candidate_sections():
    t_tree = test_utils.tree_test_sample()

    candidate_sections = t_tree.get_candidate_sections()

    assert len(candidate_sections) == 1
    assert len(candidate_sections["root"]) == 5
    assert candidate_sections["root"][0] == ["root"]
    assert candidate_sections["root"][1] == ["i"]
    assert candidate_sections["root"][2] == ["j", "k"]
    assert candidate_sections["root"][3] == ["l"]
    assert candidate_sections["root"][4] == ["m"]


def test_get_candidate_computations():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_candidate_computations("root") == ["comp01", "comp03", "comp04"]
    assert t_tree.get_candidate_computations("i") == ["comp01"]
    assert t_tree.get_candidate_computations("j") == ["comp03", "comp04"]


def test_interchange():
    t_tree = test_utils.tree_test_sample()

    t_tree.interchange("i", "j")

    assert t_tree.iterators["i"].parent_iterator == "root"
    assert t_tree.iterators["j"].parent_iterator == "root"

    assert t_tree.iterators["i"].child_iterators == ["k"]
    assert not t_tree.iterators["j"].child_iterators

    assert t_tree.iterators["k"].parent_iterator == "i"
    assert t_tree.iterators["j"].computations_list == ["comp01"]

    t_tree = test_utils.tree_test_sample()

    t_tree.interchange("j", "k")

    assert t_tree.iterators["k"].parent_iterator == "root"
    assert t_tree.iterators["k"].child_iterators == ["j"]

    assert t_tree.iterators["j"].parent_iterator == "k"
    assert t_tree.iterators["j"].child_iterators == ["l", "m"]

    assert t_tree.iterators["l"].parent_iterator == "j"
    assert t_tree.iterators["m"].parent_iterator == "j"

    t_tree = test_utils.tree_test_sample()

    t_tree.interchange("root", "j")

    assert t_tree.roots == ["j"]
    assert t_tree.iterators["j"].parent_iterator == None
    assert t_tree.iterators["j"].child_iterators == ["i", "root"]

    assert t_tree.iterators["root"].parent_iterator == "j"
    assert t_tree.iterators["root"].child_iterators == ["k"]

    assert t_tree.iterators["k"].parent_iterator == "root"


def test_get_root_of_node():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_root_of_node("i") == "root"
    assert t_tree.get_root_of_node("j") == "root"
    assert t_tree.get_root_of_node("m") == "root"


def test_get_iterator_node():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_iterator_node("i").name == "i"
    assert t_tree.get_iterator_node("l").name == "l"


def test_get_iterator_levels():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_iterator_levels(["root", "i", "j", "k", "l", "m"]) == [
        0,
        1,
        1,
        2,
        3,
        3,
    ]


def test_fuse():
    BaseConfig.init()

    t_tree = test_utils.tree_test_sample()

    t_tree.fuse("i", "j")

    assert t_tree.iterators["i"].parent_iterator == "root"
    assert t_tree.iterators["i"].child_iterators == ["k"]
    assert t_tree.iterators["i"].computations_list == ["comp01"]
    assert t_tree.iterators["i"].level == 1
    assert t_tree.iterators["k"].parent_iterator == "i"
    assert "j" not in t_tree.iterators.keys()

    t_tree = test_utils.tree_test_sample()

    t_tree.fuse("j", "i")

    assert t_tree.iterators["j"].parent_iterator == "root"
    assert t_tree.iterators["j"].child_iterators == ["k"]
    assert t_tree.iterators["j"].computations_list == ["comp01"]
    assert t_tree.iterators["j"].level == 1
    assert t_tree.iterators["k"].parent_iterator == "j"
    assert "i" not in t_tree.iterators.keys()

    multi_root = test_utils.multiple_roots_sample().tree

    multi_root.fuse("i", "i_0")

    assert multi_root.iterators["i"].parent_iterator == None
    assert multi_root.iterators["i"].child_iterators == ["j", "j_0"]
    assert multi_root.iterators["i"].computations_list == []
    assert multi_root.iterators["i"].level == 0
    assert multi_root.iterators["j_0"].parent_iterator == "i"
    assert multi_root.iterators["j"].parent_iterator == "i"
    assert "i0" not in multi_root.iterators.keys()


def test_get_computations_order_from_tree():
    BaseConfig.init()

    t_tree = test_utils.tree_test_sample()
    assert t_tree.get_computations_order_from_tree() == [
        "comp01",
        "comp03",
        "comp04",
    ]

    sample = test_utils.multiple_roots_sample()
    assert sample.tree.get_computations_order_from_tree() == [
        "A_hat",
        "x_temp",
        "x",
        "w",
    ]

    sample.tree.fuse("i_0", "i_2")
    assert sample.tree.get_computations_order_from_tree() == [
        "A_hat",
        "x_temp",
        "w",
        "x",
    ]


def test_get_iterator_of_computation():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_iterator_of_computation("comp01").name == "i"
    assert t_tree.get_iterator_of_computation("comp03").name == "l"
    assert t_tree.get_iterator_of_computation("comp04").name == "m"
