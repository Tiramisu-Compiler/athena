from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.utils.config import BaseConfig
from tests.utils import benchmark_program_test_sample


def test_apply_schedule():
    BaseConfig.init()
    test_program = benchmark_program_test_sample()

    schedule = Schedule(test_program)
    schedule.add_optimizations([Parallelization(params=["i00"], comps=["comp02"])])
    results = schedule.apply_schedule(nb_exec_tiems=10)

    assert results is not None
    assert len(results) == 10


def test_is_legal():
    BaseConfig.init()
    test_program = benchmark_program_test_sample()

    schedule = Schedule(test_program)
    schedule.add_optimizations([Parallelization(params=["i00"], comps=["comp02"])])
    legality = schedule.is_legal()

    assert legality is True


def test_copy():
    BaseConfig.init()
    original = Schedule(benchmark_program_test_sample())
    original.add_optimizations([Parallelization(params=["i00"], comps=["comp02"])])

    copy = original.copy()

    assert original is not copy
    assert original.tiramisu_program is copy.tiramisu_program
    assert original.optims_list is not copy.optims_list
    assert len(original.optims_list) == len(copy.optims_list)
    for optim in original.optims_list:
        assert optim in copy.optims_list


def test_str_representation():
    BaseConfig.init()
    test_program = benchmark_program_test_sample()

    schedule = Schedule(test_program)
    schedule.add_optimizations([Parallelization(params=["i00"], comps=["comp02"])])

    assert str(schedule) == "{comp02}:P(L0)"
