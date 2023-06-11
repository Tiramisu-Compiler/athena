import pickle

from athena.tiramisu.tiramisu_program import TiramisuProgram

from athena.tiramisu.tiramisu_iterator_node import IteratorNode

from athena.tiramisu.tiramisu_tree import TiramisuTree


def load_test_data() -> dict:
    with open("_tmp/test_data.pkl", "rb") as f:
        dataset = pickle.load(f)
    with open("_tmp/test_cpps.pkl", "rb") as f:
        cpps = pickle.load(f)
    return dataset, cpps


def tree_test_sample():
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
        # "comp02",
        "comp03",
        "comp04",
    ]
    return tiramisu_tree


def benchmark_program_test_sample():
    tiramisu_func = TiramisuProgram.from_file(
        "_tmp/function_matmul_MEDIUM.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.h",
        # "_tmp/function_blur_MINI_generator.cpp",
        # "_tmp/function_blur_MINI_wrapper.cpp",
        # "_tmp/function_blur_MINI_wrapper.h",
        load_annotations=True,
    )
    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)
    return tiramisu_func
