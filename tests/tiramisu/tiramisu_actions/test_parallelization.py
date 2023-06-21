from athena.tiramisu import tiramisu_actions
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_parallelization_init():
    parallelization = Parallelization([0], ["comp00"])
    assert parallelization.params == [0]
    assert parallelization.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    parallelization = Parallelization(["i00"], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimizations([parallelization])

    assert parallelization.tiramisu_optim_str == "comp00.tag_parallel_level(0);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    candidates = Parallelization.get_candidates(sample.tree)
    assert candidates == {"i00": [["i00"], ["i01"], ["i02"]]}


def test_legality_check():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    parallelization = Parallelization(
        ["i00"], sample.tree.get_candidate_computations("i00")
    )
    schedule = Schedule(sample)
    schedule.add_optimizations([parallelization])
    legality_string = parallelization.legality_check_string(sample.tree)
    assert (
        legality_string
        == "is_legal &= loop_parallelization_is_legal(0, {&comp02});\n    comp02.tag_parallel_level(0);\n"
    )

    sample = test_utils.multiple_roots_sample()
    schedule = Schedule(sample)
    parallelization = Parallelization(["i"], ["A_hat", "x_temp"])
    schedule.add_optimizations(
        [
            tiramisu_actions.Interchange(["i_0", "j_0"], ["x_temp"]),
            tiramisu_actions.Fusion(["i", "j_0"], ["A_hat", "x_temp"]),
            parallelization,
        ]
    )

    assert schedule.tree

    legality_string = parallelization.legality_check_string(schedule.tree)

    assert (
        legality_string
        == "is_legal &= loop_parallelization_is_legal(0, {&A_hat, &x_temp});\n    A_hat.tag_parallel_level(0);\n"
    )
