from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.distribution import Distribution
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_fusion_init():
    BaseConfig.init()
    sample = test_utils.tree_test_sample_2()

    fusion = Distribution(["j"], sample)

    assert fusion.params == ["j"]
    assert fusion.comps == [["comp05"], ["comp06"], ["comp07"], ["k"]]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.distribution_sample()
    distribution = Distribution(["j"], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([distribution])
    assert (
        distribution.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    nrm_init.then(nrm_comp,0).then(R_diag,0).then(Q_out,0).then(R_up_init,0).then(R_up,0).then(A_out,0);\n"
    )


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.distribution_sample()
    candidates = Distribution.get_candidates(sample.tree)
    assert candidates == ["k", "j"]


def test_get_fusion_levels():
    BaseConfig.init()
    t_tree = test_utils.distribution_sample()
    distribution = Distribution(["j"], t_tree.tree)
    distribution.transform_tree(t_tree.tree)
    assert distribution.get_fusion_levels(t_tree.tree.computations, t_tree.tree) == [
        0,
        0,
        0,
        0,
        0,
        0,
    ]

    t_tree = test_utils.tree_test_sample_2()
    distribution = Distribution(["j"], t_tree)
    distribution.transform_tree(t_tree)
    ordered_computations = t_tree.computations
    ordered_computations.sort(key=lambda x: t_tree.computations_absolute_order[x])
    assert distribution.get_fusion_levels(ordered_computations, t_tree) == [
        0,
        0,
        0,
        0,
        2,
    ]


def test_distribution_application():
    BaseConfig.init()

    sample = test_utils.distribution_sample()
    schedule = Schedule(sample)

    assert schedule.tree

    distribution = Distribution(["k"], schedule.tree)

    schedule.add_optimizations([distribution])

    assert (
        distribution.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    nrm_init.then(nrm_comp,-1).then(R_diag,-1).then(Q_out,-1).then(R_up_init,-1).then(R_up,1).then(A_out,1);\n"
    )
    assert not schedule.is_legal()

    sample = test_utils.distribution_sample()
    schedule = Schedule(sample)
    assert schedule.tree

    schedule.add_optimizations(
        [
            Distribution(params=["j"], tiramisu_tree=schedule.tree),
        ]
    )

    distribution = schedule.optims_list[0]

    assert (
        distribution.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    nrm_init.then(nrm_comp,0).then(R_diag,0).then(Q_out,0).then(R_up_init,0).then(R_up,0).then(A_out,0);\n"
    )

    assert schedule.is_legal()

    assert schedule.apply_schedule()


def test_transform_tree():
    BaseConfig.init()

    t_tree = test_utils.tree_test_sample_2()

    distribution = Distribution(["j"], t_tree)

    distribution.transform_tree(t_tree)

    assert "j" in t_tree.iterators
    assert "j_dist_1" in t_tree.iterators
    assert "j_dist_2" in t_tree.iterators
    assert "j_dist_3" in t_tree.iterators

    assert t_tree.iterators["j"].parent_iterator == "root"
    assert t_tree.iterators["j_dist_1"].parent_iterator == "root"
    assert t_tree.iterators["j_dist_2"].parent_iterator == "root"
    assert t_tree.iterators["j_dist_3"].parent_iterator == "root"

    assert (
        t_tree.iterators["j"].lower_bound
        == t_tree.iterators["j_dist_1"].lower_bound
        == t_tree.iterators["j_dist_2"].lower_bound
        == t_tree.iterators["j_dist_3"].lower_bound
        == 0
    )
    assert (
        t_tree.iterators["j"].upper_bound
        == t_tree.iterators["j_dist_1"].upper_bound
        == t_tree.iterators["j_dist_2"].upper_bound
        == t_tree.iterators["j_dist_3"].upper_bound
        == 256
    )

    assert t_tree.iterators["j"].computations_list == ["comp05"]
    assert t_tree.iterators["j"].child_iterators == []

    assert t_tree.iterators["j_dist_1"].computations_list == ["comp06"]
    assert t_tree.iterators["j_dist_1"].child_iterators == []

    assert t_tree.iterators["j_dist_2"].computations_list == ["comp07"]
    assert t_tree.iterators["j_dist_2"].child_iterators == []

    assert t_tree.iterators["j_dist_3"].computations_list == []
    assert t_tree.iterators["j_dist_3"].child_iterators == ["k"]
    assert t_tree.iterators["k"].parent_iterator == "j_dist_3"
