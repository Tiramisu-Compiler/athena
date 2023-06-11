import json
import logging
import time
from athena.data.dataset_actor.dataset_actor import DatasetActor
from athena.search_methods.sequential_parallelization import (
    parallelize_first_legal_outermost,
)
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree
import athena.tiramisu.tiramisu_actions as tiramisu_actions
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.tiramisu.tiramisu_program import TiramisuProgram
from athena.utils.config import BaseConfig
from tests.utils import load_test_data, tree_test_sample


if __name__ == "__main__":
    BaseConfig.init()
    # load_annotations = False
    load_annotations = True
    tiramisu_func = TiramisuProgram.from_file(
        "_tmp/function_matmul_MEDIUM.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.h",
        # "_tmp/function_blur_MINI_generator.cpp",
        # "_tmp/function_blur_MINI_wrapper.cpp",
        # "_tmp/function_blur_MINI_wrapper.h",
        load_annotations=load_annotations,
    )

    logging.info(tiramisu_func)
    tiramisu_func.tree = TiramisuTree.from_annotations(tiramisu_func.annotations)

    # t_tree = tree_test()

    # test_data, test_cpps = load_test_data()
    # get program of first key from data
    # key = list(test_data.keys())[0]
    # program_data = test_data[key]
    # program = TiramisuProgram.from_dict(key, program_data, test_cpps[key])
    # program.tree = TiramisuTree.from_annotations(program.annotations)

    schedule = parallelize_first_legal_outermost(tiramisu_func)
    logging.info(schedule)

    print(f"Unoptimized: {Schedule(tiramisu_func).apply_schedule(nb_exec_tiems=10)}")
    print(f"{schedule}: {schedule.apply_schedule(nb_exec_tiems=10)}")
    # # Create a schedule
    # schedule = Schedule(tiramisu_func)

    # # Add optimizations to the schedule
    # schedule.add_optimization(
    #     tiramisu_actions.Parallelization(params=[0], comps=["comp02"])
    # )
    # start_time = time.time()
    # legality = schedule.is_legal()
    # end_time = time.time()
    # print(f"Legality check time: {end_time - start_time}")
    # if legality:
    #     print(f"Schedule: {schedule} is legal")
    #     print(f"Optimized: {schedule.apply_schedule()}")
