from athena.tiramisu.tiramisu_actions.fusion import Fusion
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

    assert t_tree.get_iterator_subtree_computations("root") == [
        "comp01",
        "comp03",
        "comp04",
    ]
    assert t_tree.get_iterator_subtree_computations("i") == ["comp01"]
    assert t_tree.get_iterator_subtree_computations("j") == ["comp03", "comp04"]


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


def test_get_iterator_of_computation():
    t_tree = test_utils.tree_test_sample()

    assert t_tree.get_iterator_of_computation("comp01").name == "i"
    assert t_tree.get_iterator_of_computation("comp03").name == "l"
    assert t_tree.get_iterator_of_computation("comp04").name == "m"


def test_clone_subtree():
    t_tree = test_utils.tree_test_sample()

    cloned = t_tree.clone_subtree("k", suffix="_cloned")

    assert cloned.roots == ["k_cloned"]
    assert cloned.computations == ["comp03_cloned", "comp04_cloned"]
    assert cloned.computations_absolute_order == {
        "comp03_cloned": 1,
        "comp04_cloned": 2,
    }
    assert cloned.get_iterator_levels(list(cloned.iterators.keys())) == [0, 1, 1]
    assert cloned.get_iterator_of_computation("comp03_cloned").name == "l_cloned"
    assert cloned.get_iterator_of_computation("comp04_cloned").name == "m_cloned"
    assert cloned.iterators["k_cloned"].parent_iterator == None
    assert cloned.iterators["l_cloned"].parent_iterator == "k_cloned"
    assert cloned.iterators["m_cloned"].parent_iterator == "k_cloned"
    assert cloned.iterators["k_cloned"].child_iterators == ["l_cloned", "m_cloned"]
    assert cloned.iterators["l_cloned"].child_iterators == []
    assert cloned.iterators["m_cloned"].child_iterators == []


def test_update_subtree_levels():
    t_tree = test_utils.tree_test_sample()

    t_tree.update_subtree_levels("j", 0)

    assert t_tree.get_iterator_levels(["j", "k", "l", "m"]) == [0, 1, 2, 2]


def test_insert_subtree():
    t_tree = test_utils.tree_test_sample()

    cloned = t_tree.clone_subtree("k", suffix="_cloned")

    t_tree.insert_subtree(cloned, "i")

    assert t_tree.roots == ["root"]
    assert t_tree.computations == [
        "comp01",
        "comp03_cloned",
        "comp04_cloned",
        "comp03",
        "comp04",
    ]
    assert t_tree.computations_absolute_order == {
        "comp01": 1,
        "comp03_cloned": 2,
        "comp04_cloned": 3,
        "comp03": 4,
        "comp04": 5,
    }
    assert t_tree.iterators["i"].child_iterators == ["k_cloned"]
    assert t_tree.iterators["k_cloned"].parent_iterator == "i"
    assert t_tree.iterators["k_cloned"].child_iterators == ["l_cloned", "m_cloned"]
    assert t_tree.iterators["i"].computations_list == ["comp01"]
