import json
import logging
import time
from athena.data.dataset_actor.dataset_actor import DatasetActor
from athena.search_methods.sequential_parallelization import (
    parallelize_first_legal_outermost,
)
from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree
import athena.tiramisu.tiramisu_actions as tiramisu_actions
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.tiramisu.tiramisu_program import TiramisuProgram
from athena.utils.config import BaseConfig
import tests.utils as test_utils


if __name__ == "__main__":
    BaseConfig.init()

    # # Candidate sections
    # tiramisu_tree = test_utils.tree_test_sample()
    # print(tiramisu_tree.get_candidate_sections())
    # print(tiramisu_tree)

    # # Parallelization example
    # tiramisu_func = test_utils.benchmark_program_test_sample()
    # print(tiramisu_func.tree.get_candidate_sections())

    # print(Parallelization.get_candidates(tiramisu_func.tree))
    # schedule = parallelize_first_legal_outermost(tiramisu_func)
    # logging.info(schedule)

    # print(f"Unoptimized: {Schedule(tiramisu_func).apply_schedule(nb_exec_tiems=10)}")
    # print(f"{schedule}: {schedule.apply_schedule(nb_exec_tiems=10)}")

    # # Interchange example

    # interchange_program = test_utils.interchange_example()

    # print(interchange_program)

    # print(interchange_program.tree)

    # print(interchange_program.tree.get_candidate_sections())

    # candidates = Interchange.get_candidates(interchange_program.tree)
    # print(candidates)

    # # paralel_sched = parallelize_first_legal_outermost(interchange_program)
    # paralel_sched = Schedule(interchange_program)
    # paralel_sched.add_optimization(Parallelization([0], ["comp00"]))
    # print(paralel_sched)
    # print(paralel_sched.is_legal())

    # paralel_sched = Schedule(interchange_program)
    # paralel_sched.add_optimization(Parallelization([1], ["comp00"]))
    # print(paralel_sched)
    # print(paralel_sched.is_legal())

    # print(paralel_sched.apply_schedule(nb_exec_tiems=10))

    # legal_par = Schedule(interchange_program)
    # legal_par.add_optimization(Interchange(["i0", "i1"], ["comp00"]))
    # legal_par.add_optimization(Parallelization([0], ["comp00"]))
    # print(legal_par.is_legal())
    # print(legal_par.apply_schedule(nb_exec_tiems=10))

    # for root in candidates:
    #     for params in candidates[root]:
    #         schedule = Schedule(interchange_program)
    #         schedule.add_optimization(
    #             Interchange(
    #                 params=params,
    #                 comps=Interchange.get_candidate_computations(
    #                     params[0], interchange_program.tree
    #                 ),
    #             )
    #         )

    #         print(schedule)
    #         print(schedule.is_legal())
    #         print("\n\n")

    # Skewing example

    skewing_program = test_utils.skewing_example()

    print(skewing_program)

    print(tiramisu_actions.Skewing.get_candidates(skewing_program.tree))

    print(skewing_program.tree)

    factors = tiramisu_actions.Skewing.get_factors(
        loops=["i0", "i1"], current_schedule=[], tiramisu_program=skewing_program
    )

    schedule = Schedule(skewing_program)
    params = ["i0", "i1"] + ([str(factor) for factor in factors])
    schedule.add_optimization(tiramisu_actions.Skewing(params=params, comps=["comp00"]))
    print(schedule)
    print(schedule.is_legal())
    print(schedule.apply_schedule(nb_exec_tiems=10))
