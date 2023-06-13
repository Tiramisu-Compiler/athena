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
    parallelization = Parallelization([0], ["comp00"])
    schedule = Schedule(sample)
    schedule.add_optimization(parallelization)

    assert parallelization.tiramisu_optim_str == "\n\tcomp00.tag_parallel_level(0);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.benchmark_program_test_sample()
    candidates = Parallelization.get_candidates(sample.tree)
    assert candidates == {"i00": [["i00"], ["i01"], ["i02"]]}
