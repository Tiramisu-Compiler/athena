from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Reversal(TiramisuAction):
    """
    Reversal optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Reversal only takes one parameters of the loop to reverse
        assert len(params) == 1

        super().__init__(type=TiramisuActionType.REVERSAL, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        level = tiramisu_tree.iterators[self.params[0]].level
        for comp in self.comps:
            self.tiramisu_optim_str += f"{comp}.loop_reversal({level});\n"

        self.str_representation = "R(L" + str(level) + ")"

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> Dict[str, List[str]]:
        candidates: Dict[str, List[str]] = {}
        for root in program_tree.roots:
            candidates[root] = [root] + program_tree.iterators[root].child_iterators
            nodes_to_visit = program_tree.iterators[root].child_iterators.copy()

            while nodes_to_visit:
                node = nodes_to_visit.pop(0)
                node_children = program_tree.iterators[node].child_iterators
                nodes_to_visit.extend(node_children)
                candidates[root].extend(node_children)

        return candidates

    def transform_tree(self, program_tree: TiramisuTree):
        node = program_tree.iterators[self.params[0]]

        # Reverse the loop bounds
        node.lower_bound, node.upper_bound = node.upper_bound, node.lower_bound
