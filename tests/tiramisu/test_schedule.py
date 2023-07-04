from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.parallelization import Parallelization
from athena.tiramisu import tiramisu_actions
from athena.utils.config import BaseConfig
import tests.utils as test_utils
from tests.utils import benchmark_program_test_sample


def test_apply_schedule():
    BaseConfig.init()
    test_program = benchmark_program_test_sample()

    schedule = Schedule(test_program)
    schedule.add_optimizations(
        [Parallelization(params=["i00"], tiramisu_tree=schedule.tree)]
    )
    results = schedule.apply_schedule(nb_exec_tiems=10)

    assert results is not None
    assert len(results) == 10


def test_is_legal():
    BaseConfig.init()
    test_program = benchmark_program_test_sample()

    schedule = Schedule(test_program)
    schedule.add_optimizations(
        [Parallelization(params=["i00"], tiramisu_tree=schedule.tree)]
    )
    legality = schedule.is_legal()

    assert legality is True


def test_copy():
    BaseConfig.init()
    original = Schedule(benchmark_program_test_sample())
    original.add_optimizations(
        [Parallelization(params=["i00"], tiramisu_tree=original.tree)]
    )

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
    schedule.add_optimizations(
        [Parallelization(params=["i00"], tiramisu_tree=schedule.tree)]
    )

    assert str(schedule) == "P(L0,comps=['comp02'])"


def test_from_sched_str():
    BaseConfig.init()

    test_program = test_utils.multiple_roots_sample()

    schedule = Schedule(test_program)

    schedule.add_optimizations(
        [
            Parallelization(params=["i"], tiramisu_tree=schedule.tree),
            tiramisu_actions.Interchange(
                params=["i_0", "j_0"], tiramisu_tree=schedule.tree
            ),
            tiramisu_actions.Fusion(params=["i", "j_0"], tiramisu_tree=schedule.tree),
            tiramisu_actions.Tiling2D(
                params=["i_2", "j_1", 4, 4], tiramisu_tree=schedule.tree
            ),
            tiramisu_actions.Unrolling(params=["i_1", 4], tiramisu_tree=schedule.tree),
            tiramisu_actions.Reversal(params=["i_1"], tiramisu_tree=schedule.tree),
        ]
    )

    sched_str = str(schedule)

    new_schedule = Schedule.from_sched_str(sched_str, test_program)

    assert new_schedule is not None

    assert len(new_schedule.optims_list) == len(schedule.optims_list)

    for idx, optim in enumerate(schedule.optims_list):
        assert optim == new_schedule.optims_list[idx]

    schedule = Schedule(test_program)

    schedule.add_optimizations(
        [
            tiramisu_actions.Skewing(
                params=["i_0", "j_0", 1, 1], tiramisu_tree=schedule.tree
            ),
        ]
    )

    sched_str = str(schedule)

    new_schedule = Schedule.from_sched_str(sched_str, test_program)

    assert new_schedule is not None
    assert len(new_schedule.optims_list) == len(schedule.optims_list)

    for idx, optim in enumerate(schedule.optims_list):
        assert optim == new_schedule.optims_list[idx]

    test_program = test_utils.tiling_3d_sample()

    schedule = Schedule(test_program)

    schedule.add_optimizations(
        [
            tiramisu_actions.Tiling3D(["i0", "i1", "i2", 4, 4, 4], schedule.tree),
        ]
    )

    sched_str = str(schedule)

    new_schedule = Schedule.from_sched_str(sched_str, test_program)

    assert new_schedule is not None
    assert len(new_schedule.optims_list) == len(schedule.optims_list)

    for idx, optim in enumerate(schedule.optims_list):
        assert optim == new_schedule.optims_list[idx]
