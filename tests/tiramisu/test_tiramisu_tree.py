from tests.utils import load_test_data, tree_test_sample
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree


def test_from_annotations():
    data, _, _ = load_test_data()
    # get program of first key from data
    program = data[list(data.keys())[0]]
    tiramisu_tree = TiramisuTree.from_annotations(program["program_annotation"])
    assert len(tiramisu_tree.roots) == 1


def test_get_candidate_sections():
    t_tree = tree_test_sample()

    candidate_sections = t_tree.get_candidate_sections()

    assert len(candidate_sections) == 1
    assert len(candidate_sections["root"]) == 5
    assert candidate_sections["root"][0] == ["root"]
    assert candidate_sections["root"][1] == ["i"]
    assert candidate_sections["root"][2] == ["j", "k"]
    assert candidate_sections["root"][3] == ["l"]
    assert candidate_sections["root"][4] == ["m"]


def test_get_candidate_computations():
    t_tree = tree_test_sample()

    assert t_tree.get_candidate_computations("root") == ["comp01", "comp03", "comp04"]
    assert t_tree.get_candidate_computations("i") == ["comp01"]
    assert t_tree.get_candidate_computations("j") == ["comp03", "comp04"]
