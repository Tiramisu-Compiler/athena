from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.fusion import Fusion
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
    schedule.add_optimization(fusion)
    assert fusion.tiramisu_optim_str == "\n\tcomp03.then(comp04,3);"


def test_get_candidates():
    BaseConfig.init()
    sample = test_utils.fusion_sample()
    candidates = Fusion.get_candidates(sample.tree)
    assert candidates == [("i", "j"), ("l", "m")]
