import pytest

import tests.utils as test_utils
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.interchange import Interchange
from athena.tiramisu.tiramisu_actions.tiling_2d import Tiling2D
from athena.tiramisu.tiramisu_actions.tiramisu_action import CannotApplyException
from athena.utils.config import BaseConfig
from tests.utils import interchange_example


def test_interchange_init():
    BaseConfig.init()
    sample = interchange_example()
    interchange = Interchange(["i0", "i1"], sample.tree)
    assert [node.name for node in interchange.params] == ["i0", "i1"]
    assert interchange.comps == ["comp00"]


def test_set_string_representations():
    BaseConfig.init()
    sample = interchange_example()
    interchange = Interchange(["i0", "i1"], sample.tree)
    schedule = Schedule(sample)
    schedule.add_optimizations([interchange])
    assert interchange.tiramisu_optim_str == "comp00.interchange(0,1);\n"


def test_get_candidates():
    BaseConfig.init()
    sample = interchange_example()
    candidates = Interchange.get_candidates(sample.tree)
    assert candidates == {"i0": [("i0", "i1"), ("i0", "i2"), ("i1", "i2")]}


def test_legality_check():
    BaseConfig.init()
    sample = interchange_example()
    schedule = Schedule(sample)
    assert schedule.tree
    schedule.add_optimizations(
        [Interchange([("comp00", 0), ("comp00", 1)], schedule.tree)]
    )
    legality_string = schedule.optims_list[0].legality_check_string
    assert legality_string == "comp00.interchange(0,1);\n"
