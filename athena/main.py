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
    BaseConfig.init(logging_level=logging.ERROR)

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

    # # Skewing example

    # skewing_program = test_utils.skewing_example()

    # print(skewing_program)

    # par_schedule = Schedule(skewing_program)

    # par_schedule.add_optimization(Parallelization([0], ["comp00"]))

    # print(par_schedule)

    # print(par_schedule.is_legal())

    # print(tiramisu_actions.Skewing.get_candidates(skewing_program.tree))

    # print(skewing_program.tree)

    # factors = tiramisu_actions.Skewing.get_factors(
    #     loops=["i0", "i1"], current_schedule=[], tiramisu_program=skewing_program
    # )

    # schedule = Schedule(skewing_program)
    # params = ["i0", "i1"] + ([str(factor) for factor in factors])
    # schedule.add_optimization(tiramisu_actions.Skewing(params=params, comps=["comp00"]))
    # print(schedule)
    # print(schedule.is_legal())
    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # # Reversal example

    # reversal_program = test_utils.reversal_sample()

    # print(reversal_program)

    # print(reversal_program.tree)

    # print(tiramisu_actions.Reversal.get_candidates(reversal_program.tree))

    # par_schedule = Schedule(reversal_program)
    # par_schedule.add_optimization(Parallelization([0], ["comp00"]))
    # print(par_schedule)

    # print(par_schedule.is_legal())

    # # print(par_schedule.apply_schedule(nb_exec_tiems=10))

    # schedule = Schedule(reversal_program)

    # schedule.add_optimization(
    #     tiramisu_actions.Reversal(params=["i1"], comps=["comp00"])
    # )
    # print(schedule)

    # print(schedule.is_legal())

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # schedule.add_optimization(
    #     tiramisu_actions.Interchange(params=["i0", "i1"], comps=["comp00"])
    # )

    # schedule.add_optimization(
    #     tiramisu_actions.Parallelization(params=[0], comps=["comp00"])
    # )
    # print(schedule)
    # print(schedule.is_legal())
    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # # Unrolling example

    # unrolling_program = test_utils.unrolling_sample()

    # print(unrolling_program)

    # print(unrolling_program.tree)

    # print(tiramisu_actions.Unrolling.get_candidates(unrolling_program.tree))

    # par_schedule = Schedule(unrolling_program)

    # par_schedule.add_optimization(
    #     tiramisu_actions.Parallelization(params=[0], comps=["comp00"])
    # )

    # print(par_schedule)

    # print(par_schedule.is_legal())

    # # print(par_schedule.apply_schedule(nb_exec_tiems=10))

    # schedule = Schedule(unrolling_program)

    # schedule.add_optimization(
    #     tiramisu_actions.Unrolling(params=["i1", 4], comps=["comp00"])
    # )
    # print(schedule)

    # print(schedule.is_legal())

    # schedule.add_optimization(
    #     tiramisu_actions.Interchange(params=["i0", "i1"], comps=["comp00"])
    # )

    # schedule.add_optimization(
    #     tiramisu_actions.Parallelization(params=[0], comps=["comp00"])
    # )

    # print(schedule)

    # print(schedule.is_legal())

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # print("Interchange with parallelization")

    # schedule = Schedule(unrolling_program)

    # schedule.add_optimization(
    #     tiramisu_actions.Interchange(params=["i0", "i1"], comps=["comp00"])
    # )

    # schedule.add_optimization(
    #     tiramisu_actions.Parallelization(params=[0], comps=["comp00"])
    # )

    # print(schedule)

    # print(schedule.is_legal())

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # # Tiling2D example

    # tiling_program = test_utils.tiling_2d_sample()

    # print(tiling_program)

    # print(tiling_program.tree)

    # print(tiramisu_actions.Tiling2D.get_candidates(tiling_program.tree))

    # schedule = Schedule(tiling_program)

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # schedule.add_optimization(
    #     tiramisu_actions.Tiling2D(params=["i0", "i1", 32, 32], comps=["comp00"])
    # )

    # print(schedule)

    # print(schedule.is_legal())

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # # Tiling3D example

    # tiling_program = test_utils.tiling_3d_sample()

    # print(tiling_program)

    # print(tiling_program.tree)

    # print(tiramisu_actions.Tiling3D.get_candidates(tiling_program.tree))

    # schedule = Schedule(tiling_program)

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # schedule.add_optimization(
    #     tiramisu_actions.Tiling3D(
    #         params=["i0", "i1", "i2", 32, 32, 32], comps=["comp00"]
    #     )
    # )

    # print(schedule)

    # print(schedule.is_legal())

    # print(schedule.apply_schedule(nb_exec_tiems=10))

    # Fusion example

    t_tree = test_utils.multiple_roots_sample()

    print(t_tree)

    print(t_tree.tree)
