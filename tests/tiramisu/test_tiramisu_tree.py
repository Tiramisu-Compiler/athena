from tests.utils import load_test_data, tree_test_sample
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree


def test_get_candidate_sections():
    tiramisu_tree = TiramisuTree()
    tiramisu_tree.add_root("root")
    tiramisu_tree.iterators = {
        "root": IteratorNode(
            name="root",
            parent_iterator=None,
            lower_bound=0,
            upper_bound=10,
            child_iterators=["i", "j"],
            computations_list=[],
        ),
        "i": IteratorNode(
            name="i",
            parent_iterator="root",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp01"],
        ),
        "j": IteratorNode(
            name="j",
            parent_iterator="root",
            lower_bound=0,
            upper_bound=10,
            child_iterators=["k"],
            computations_list=[],
        ),
        "k": IteratorNode(
            name="k",
            parent_iterator="j",
            lower_bound=0,
            upper_bound=10,
            child_iterators=["l", "m"],
            computations_list=[],
        ),
        "l": IteratorNode(
            name="l",
            parent_iterator="k",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp03"],
        ),
        "m": IteratorNode(
            name="m",
            parent_iterator="k",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp04"],
        ),
    }
    tiramisu_tree.computations = [
        "comp01",
        "comp02",
        "comp03",
        "comp04",
    ]

    candidate_sections = tiramisu_tree.get_candidate_sections()

    assert len(candidate_sections) == 5
    assert candidate_sections[0] == ["root"]
    assert candidate_sections[1] == ["i"]
    assert candidate_sections[2] == ["j", "k"]
    assert candidate_sections[3] == ["l"]
    assert candidate_sections[4] == ["m"]


def test_from_annotations():
    data, _ = load_test_data()
    # get program of first key from data
    program = data[list(data.keys())[0]]
    tiramisu_tree = TiramisuTree.from_annotations(program["program_annotation"])
    assert len(tiramisu_tree.roots) == 1


def test_get_candidate_sections():
    t_tree = tree_test_sample()

    candidate_sections = t_tree.get_candidate_sections()

    assert len(candidate_sections) == 5
    assert candidate_sections[0] == ["root"]
    assert candidate_sections[1] == ["i"]
    assert candidate_sections[2] == ["j", "k"]
    assert candidate_sections[3] == ["l"]
    assert candidate_sections[4] == ["m"]
