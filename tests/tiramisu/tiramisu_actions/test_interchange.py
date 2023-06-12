from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.utils.config import BaseConfig
from tests.utils import interchange_example


def test_interchange_init():
    interchange = Interchange(["i0", "i1"], ["comp00"])
    assert interchange.params == ["i0", "i1"]
    assert interchange.comps == ["comp00"]


def test_get_tiramisu_optim_str():
    BaseConfig.init()
    sample = interchange_example()
    interchange = Interchange(["i0", "i1"], ["comp00"])
    assert (
        interchange.get_tiramisu_optim_str(sample.tree)
        == "comp00.interchange(0,1);\n\t"
    )


def test_get_candidates():
    BaseConfig.init()
    sample = interchange_example()
    candidates = Interchange.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1"), ("i0", "i2"), ("i1", "i2")]}
