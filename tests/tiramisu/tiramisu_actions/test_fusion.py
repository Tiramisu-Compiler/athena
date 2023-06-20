from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.fusion import Fusion
from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.utils.config import BaseConfig
import tests.utils as test_utils


def test_fusion_init():
    fusion = Fusion(["i0", "i1"], ["comp00", "comp01"])
    assert fusion.params == ["i0", "i1"]
    assert fusion.comps == ["comp00", "comp01"]


def test_set_string_representations():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    fusion = Fusion(["l", "m"], ["comp03", "comp04"])
    schedule = Schedule(sample)
    schedule.add_optimizations([fusion])
    assert fusion.tiramisu_optim_str == "\n\tcomp01.then(comp03,0).then(comp04,3);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    candidates = Fusion.get_candidates(sample.tree)
    assert candidates == [("i", "j"), ("l", "m")]


def test_get_fusion_levels():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    fusion = Fusion(["l", "m"], ["comp03", "comp04"])
    sample.tree.fuse("l", "m")
    assert fusion.get_fusion_levels(
        sample.tree.get_computations_order_from_tree(), sample.tree
    ) == [0, 3]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i", "i_0"], ["A_hat", "x_temp"])
    sample.tree.fuse("i", "i_0")
    assert fusion.get_fusion_levels(
        sample.tree.get_computations_order_from_tree(), sample.tree
    ) == [0, -1, -1]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i_1", "i_2"], ["x", "w"])
    sample.tree.fuse("i_1", "i_2")
    assert fusion.get_fusion_levels(
        sample.tree.get_computations_order_from_tree(), sample.tree
    ) == [-1, -1, 0]

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i_0", "i_2"], ["x_temp", "w"])
    sample.tree.fuse("i_0", "i_2")
    assert fusion.get_fusion_levels(
        sample.tree.get_computations_order_from_tree(), sample.tree
    ) == [-1, 0, -1]
    sample.tree.fuse("j_0", "j_1")
    assert fusion.get_fusion_levels(
        sample.tree.get_computations_order_from_tree(), sample.tree
    ) == [-1, 1, -1]


def test_fusion_application():
    BaseConfig.init()

    sample = test_utils.multiple_roots_sample()
    fusion = Fusion(["i", "i_0"], ["A_hat", "x_temp"])
    schedule = Schedule(sample)

    schedule.add_optimizations([fusion])

    assert (
        fusion.tiramisu_optim_str == "\n\tA_hat.then(x_temp,0).then(x,-1).then(w,-1);"
    )
    assert not schedule.is_legal()

    schedule = Schedule(sample)
    fusion = Fusion(params=["i", "j_0"], comps=["A_hat", "x_temp"])
    schedule.add_optimizations(
        [
            Interchange(params=["i_0", "j_0"], comps=["x_temp"]),
            fusion,
        ]
    )

    assert (
        fusion.tiramisu_optim_str == "\n\tA_hat.then(x_temp,0).then(x,-1).then(w,-1);"
    )

    assert schedule.is_legal()

    assert schedule.apply_schedule()
