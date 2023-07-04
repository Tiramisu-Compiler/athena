from athena.tiramisu import tiramisu_actions
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_parallelization_init():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    parallelization = Parallelization(["i00"], sample.tree)
    assert parallelization.params == ["i00"]
    assert parallelization.comps == ["comp02"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    parallelization = Parallelization(["i00"], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([parallelization])

    assert parallelization.tiramisu_optim_str == "comp02.tag_parallel_level(0);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    candidates = Parallelization.get_candidates(sample.tree)
    assert candidates == {"i00": [["i00"], ["i01"], ["i02"]]}


def test_legality_check():
    BaseConfig.init()

    # sample = test_utils.benchmark_program_test_sample()
    # schedule = Schedule(sample)
    # assert schedule.tree
    # parallelization = Parallelization(["i00"], schedule.tree)

    # schedule.add_optimizations([parallelization])
    # legality_string = schedule.optims_list[0].legality_check_string
    # assert (
    #     legality_string
    #     == "is_legal &= loop_parallelization_is_legal(0, {&comp02});\n    comp02.tag_parallel_level(0);\n"
    # )

    sample = test_utils.multiple_roots_sample()
    schedule = Schedule(sample)
    assert schedule.tree

    schedule.add_optimizations(
        [
            tiramisu_actions.Interchange(["i_0", "j_0"], schedule.tree),
            tiramisu_actions.Fusion(["i", "j_0"], schedule.tree),
        ]
    )

    parallelization = Parallelization(["i"], schedule.tree)

    schedule.add_optimizations([parallelization])

    assert schedule.tree

    legality_string = schedule.optims_list[2].legality_check_string

    assert (
        legality_string
        == "is_legal &= loop_parallelization_is_legal(0, {&A_hat, &x_temp});\n    A_hat.tag_parallel_level(0);\n"
    )
