import pickle
from typing import Tuple

from athena.tiramisu.tiramisu_program import TiramisuProgram

from athena.tiramisu.tiramisu_iterator_node import IteratorNode

from athena.tiramisu.tiramisu_tree import TiramisuTree


def load_test_data() -> Tuple[dict, dict]:
    with open("_tmp/enabling_parallelism.pkl", "rb") as f:
        dataset = pickle.load(f)
    with open("_tmp/enabling_parallelism_cpps.pkl", "rb") as f:
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
        # "_tmp/function_matmul_MEDIUM_wrapper.cpp",
        # "_tmp/function_matmul_MEDIUM_wrapper.h",
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
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function837782",
        data=test_data["function837782"],
        original_str=test_cpps["function837782"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def skewing_example() -> TiramisuProgram:
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function550013",
        data=test_data["function550013"],
        original_str=test_cpps["function550013"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def reversal_sample() -> TiramisuProgram:
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function824914",
        data=test_data["function824914"],
        original_str=test_cpps["function824914"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def unrolling_sample() -> TiramisuProgram:
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function552581",
        data=test_data["function552581"],
        original_str=test_cpps["function552581"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def tiling_2d_sample() -> TiramisuProgram:
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function554520",
        data=test_data["function554520"],
        original_str=test_cpps["function554520"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def tiling_3d_sample() -> TiramisuProgram:
    test_data, test_cpps = load_test_data()

    tiramisu_func = TiramisuProgram.from_dict(
        name="function608722",
        data=test_data["function608722"],
        original_str=test_cpps["function608722"],
    )
    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    return tiramisu_func


def tiling_3d_tree_sample() -> TiramisuTree:
    tiramisu_tree = TiramisuTree()
    tiramisu_tree.add_root("root")
    tiramisu_tree.iterators = {
        "root": IteratorNode(
            name="root",
            parent_iterator=None,
            lower_bound=0,
            upper_bound=10,
            child_iterators=["j"],
            computations_list=[],
            level=0,
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
            child_iterators=["l"],
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
    }
    tiramisu_tree.computations = [
        "comp03",
    ]
    return tiramisu_tree


def fusion_sample():
    tiramisu_prog = TiramisuProgram()

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

    tiramisu_prog.tree = tiramisu_tree
    return tiramisu_prog


def random_program_sample():
    tiramisu_func = TiramisuProgram.from_file(
        "_tmp/test.cpp",
        # "_tmp/function_blur_MINI_generator.cpp",
        # "_tmp/function_blur_MINI_wrapper.cpp",
        # "_tmp/function_blur_MINI_wrapper.h",
        load_annotations=True,
    )

    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)
    return tiramisu_func


def multiple_roots_sample():
    tiramisu_func = TiramisuProgram.from_file(
        "_tmp/function_gemver_MINI_generator.cpp",
        load_annotations=True,
    )

    if tiramisu_func.annotations is None:
        raise ValueError("Annotations not found")

    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)
    return tiramisu_func
