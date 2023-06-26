from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.fusion import Fusion
from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_fusion_init():
    BaseConfig.init()
    sample = test_utils.fusion_sample()

    fusion = Fusion(["l", "m"], sample.tree)

    assert fusion.params == ["l", "m"]
    for comp in fusion.comps:
        assert comp in ["comp03", "comp04"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    fusion = Fusion(["l", "m"], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([fusion])
    assert (
        fusion.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    comp01.then(comp03,0).then(comp04,3);\n"
    )


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    candidates = Fusion.get_candidates(sample.tree)
    assert candidates == [("i", "j"), ("l", "m")]


def test_get_fusion_levels():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    fusion = Fusion(["l", "m"], sample.tree)
    fusion.transform_tree(sample.tree)
    assert fusion.get_fusion_levels(sample.tree.computations, sample.tree) == [0, 3]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i", "i_0"], sample.tree)
    fusion.transform_tree(sample.tree)
    assert fusion.get_fusion_levels(sample.tree.computations, sample.tree) == [
        0,
        -1,
        -1,
    ]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i_1", "i_2"], sample.tree)
    fusion.transform_tree(sample.tree)
    assert fusion.get_fusion_levels(sample.tree.computations, sample.tree) == [
        -1,
        -1,
        0,
    ]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i_0", "i_2"], sample.tree)
    fusion.transform_tree(sample.tree)

    assert fusion.get_fusion_levels(
        sample.tree.computations,
        sample.tree,
    ) == [
        -1,
        0,
        -1,
    ]

    # sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["j_0", "j_1"], sample.tree)
    fusion.transform_tree(sample.tree)
    assert fusion.get_fusion_levels(sample.tree.computations, sample.tree) == [
        -1,
        1,
        -1,
    ]


def test_fusion_application():
    BaseConfig.init()

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i", "i_0"], sample.tree)
    schedule = Schedule(sample)

    schedule.add_optimizations([fusion])

    assert (
        fusion.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    A_hat.then(x_temp,0).then(x,-1).then(w,-1);\n"
    )
    assert not schedule.is_legal()

    schedule = Schedule(sample)
    fusion = Fusion(params=["i", "j_0"], tiramisu_tree=sample.tree)
    schedule.add_optimizations(
        [
            Interchange(params=["i_0", "j_0"], tiramisu_tree=sample.tree),
            fusion,
        ]
    )

    assert (
        fusion.tiramisu_optim_str
        == "clear_implicit_function_sched_graph();\n    A_hat.then(x_temp,0).then(x,-1).then(w,-1);\n"
    )

    assert schedule.is_legal()

    assert schedule.apply_schedule()


def test_transform_tree():
    BaseConfig.init()

    t_tree = test_utils.tree_test_sample()

    fusion = Fusion(["i", "j"], t_tree)

    fusion.transform_tree(t_tree)

    assert t_tree.iterators["i"].parent_iterator == "root"
    assert t_tree.iterators["i"].child_iterators == ["k"]
    assert t_tree.iterators["i"].computations_list == ["comp01"]
    assert t_tree.iterators["i"].level == 1
    assert t_tree.iterators["k"].parent_iterator == "i"
    assert "j" not in t_tree.iterators.keys()

    t_tree = test_utils.tree_test_sample()

    fusion = Fusion(["j", "i"], t_tree)

    fusion.transform_tree(t_tree)

    assert t_tree.iterators["j"].parent_iterator == "root"
    assert t_tree.iterators["j"].child_iterators == ["k"]
    assert t_tree.iterators["j"].computations_list == ["comp01"]
    assert t_tree.iterators["j"].level == 1
    assert t_tree.iterators["k"].parent_iterator == "j"
    assert "i" not in t_tree.iterators.keys()

    multi_root = test_utils.multiple_roots_sample().tree

    fusion = Fusion(["i", "i_0"], multi_root)
    fusion.transform_tree(multi_root)

    assert multi_root.iterators["i"].parent_iterator == None
    assert multi_root.iterators["i"].child_iterators == ["j", "j_0"]
    assert multi_root.iterators["i"].computations_list == []
    assert multi_root.iterators["i"].level == 0
    assert multi_root.iterators["j_0"].parent_iterator == "i"
    assert multi_root.iterators["j"].parent_iterator == "i"
    assert "i0" not in multi_root.iterators.keys()
