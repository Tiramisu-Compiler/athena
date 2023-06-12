import pickle
from typing import Tuple

from athena.tiramisu.tiramisu_program import TiramisuProgram

from athena.tiramisu.tiramisu_iterator_node import IteratorNode

from athena.tiramisu.tiramisu_tree import TiramisuTree


def load_test_data() -> Tuple[dict, dict, dict]:
    with open("_tmp/enabling_parallelism.pkl", "rb") as f:
        dataset = pickle.load(f)
    with open("_tmp/enabling_parallelism_cpps.pkl", "rb") as f:
        cpps = pickle.load(f)
    with open("_tmp/enabling_parallelism_wrappers.pkl", "rb") as f:
        wrappers = pickle.load(f)
    return dataset, cpps, wrappers


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
            level=0,
        ),
        "i": IteratorNode(
            name="i",
            parent_iterator="root",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp01"],
            level=1,
        ),
        "j": IteratorNode(
            name="j",
            parent_iterator="root",
            lower_bound=0,
            upper_bound=10,
            child_iterators=["k"],
            computations_list=[],
            level=1,
        ),
        "k": IteratorNode(
            name="k",
            parent_iterator="j",
            lower_bound=0,
            upper_bound=10,
            child_iterators=["l", "m"],
            computations_list=[],
            level=2,
        ),
        "l": IteratorNode(
            name="l",
            parent_iterator="k",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp03"],
            level=3,
        ),
        "m": IteratorNode(
            name="m",
            parent_iterator="k",
            lower_bound=0,
            upper_bound=10,
            child_iterators=[],
            computations_list=["comp04"],
            level=3,
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

    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)
    return tiramisu_func


def interchange_example() -> TiramisuProgram:
    test_data, test_cpps, test_wrappers = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function837782",
        data=test_data["function837782"],
        original_str=test_cpps["function837782"],
        wrappers=test_wrappers["function837782"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func
