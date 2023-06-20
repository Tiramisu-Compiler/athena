from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Unrolling(TiramisuAction):
    """
    Unrolling optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Unrolling only takes two parameters, the loop level and the factor
        assert len(params) == 2

        super().__init__(type=TiramisuActionType.UNROLLING, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_level = tiramisu_tree.iterators[self.params[0]].level
        unrolling_factor = self.params[1]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"\n\t{comp}.unroll({loop_level},{unrolling_factor});"
            )
        self.str_representation = (
            "U(L" + str(loop_level) + "," + str(unrolling_factor) + ")"
        )

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> List[str]:
        candidates: List[str] = []

        for iterator in program_tree.iterators:
            iterator_node = program_tree.iterators[iterator]
            if not iterator_node.child_iterators and iterator_node.computations_list:
                candidates.append(iterator)

        return candidates
