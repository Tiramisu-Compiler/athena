from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.schedule import Schedule

from enum import Enum
from typing import List


from athena.tiramisu.tiramisu_program import TiramisuProgram


class TiramisuActionType(Enum):
    """The type of an optimization command."""

    INTERCHANGE = 0
    TILING_2D = 1
    PARALLELIZATION = 2
    SKEWING = 3
    UNROLLING = 4
    FUSION = 5
    REVERSAL = 6
    TILING_3D = 7


class TiramisuAction:
    """
    Base class for all optimization commands.

    Attributes:
    ----------

    `type`: `TiramisuActionType`
        The type of the optimization command.

    `params`: `list`
        The parameters of the optimization command.

    `comps`: `list`
        The computations that are concerned by the optimization command.

    """

    def __init__(
        self,
        type: TiramisuActionType,
        params: list | dict,
        comps: List[str],
    ):
        self.params = params
        # A list of concerned computations of the actions
        self.comps = comps
        # The type of the action
        self.type = type
        # The tiramisu code that represents the action
        self.tiramisu_optim_str = ""
        # The str representation of the action
        self.str_representation = ""

    def set_string_representations(self, tiramisu_tree: TiramisuTree) -> str:
        """Convert the optimization command into Tiramisu code.
        Returns:
            str: The tiramisu snippet that represents the optimization command.
        """
        raise NotImplementedError

    #     if self.type == ActionType.INTERCHANGE:
    #         interchange_str = (
    #             ".interchange(" + ",".join([str(p) for p in self.params_list]) + ");"
    #         )
    #         optim_str = ""
    #         for comp in self.comps:
    #             optim_str += "\n\t{}".format(comp) + interchange_str
    #         return optim_str
    #     elif self.type == ActionType.SKEWING:
    #         assert len(self.params_list) == 4
    #         skewing_str = ".skew(" + ",".join([str(p) for p in self.params_list]) + ");"
    #         optim_str = ""
    #         for comp in self.comps:
    #             optim_str += "\n\t{}".format(comp) + skewing_str
    #         return optim_str
    #     elif self.type == ActionType.PARALLELIZATION:
    #         assert len(self.params_list) == 1
    #         return (
    #             "\n\t"
    #             + self.comps[0]
    #             + ".tag_parallel_level("
    #             + str(self.params_list[0])
    #             + ");"
    #         )
    #     elif self.type == ActionType.TILING:
    #         assert len(self.params_list) == 4 or len(self.params_list) == 6
    #         tiling_str = ".tile(" + ",".join([str(p) for p in self.params_list]) + ");"
    #         optim_str = ""
    #         for comp in self.comps:
    #             optim_str += "\n\t{}".format(comp) + tiling_str
    #         return optim_str
    #     elif self.type == ActionType.UNROLLING:
    #         optim_str = ""
    #         for comp in self.comps:
    #             unrolling_str = (
    #                 ".unroll("
    #                 + ",".join([str(p) for p in self.params_list[comp]])
    #                 + ");"
    #             )
    #             optim_str += "\n\t{}".format(comp) + unrolling_str
    #         return optim_str
    #     elif self.type == ActionType.REVERSAL:
    #         reversal_str = ".loop_reversal(" + str(self.params_list[0]) + ");"
    #         optim_str = ""
    #         for comp in self.comps:
    #             optim_str += "\n\t{}".format(comp) + reversal_str
    #         return optim_str
    #     elif self.type == ActionType.FUSION:
    #         # TODO : Recheck the right command for this
    #         optim_str = ""
    #         # prev_comp = self.comps[0]
    #         # for comp in self.comps[1:]:
    #         #     optim_str += ("\n\t {}".format(prev_comp) + ".then(" +
    #         #                   str(comp) + "," + str(self.params_list[0]) +
    #         #                   ");")
    #         #     prev_comp = comp
    #         optim_str = "\n\t" + self.comps[0]
    #         for comp in self.comps[1:]:
    #             optim_str += ".then(" + comp + "," + str(self.params_list[0]) + ")"
    #         optim_str += ";"
    #         return optim_str

    def is_interchange(self) -> bool:
        return self.type == TiramisuActionType.INTERCHANGE

    def is_tiling(self) -> bool:
        return self.type == TiramisuActionType.TILING

    def is_parallelization(self) -> bool:
        return self.type == TiramisuActionType.PARALLELIZATION

    def is_skewing(self) -> bool:
        return self.type == TiramisuActionType.SKEWING

    def is_unrolling(self) -> bool:
        return self.type == TiramisuActionType.UNROLLING

    def is_fusion(self) -> bool:
        return self.type == TiramisuActionType.FUSION

    def is_reversal(self) -> bool:
        return self.type == TiramisuActionType.REVERSAL

    def get_candidates(self, program_tree: TiramisuTree) -> list:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"Action(type={self.type}, params={self.params}, comps={self.comps})"

    def __repr__(self) -> str:
        return self.__str__()
