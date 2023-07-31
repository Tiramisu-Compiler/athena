from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Dict, List, Tuple

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree

from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    CannotApplyException,
    IteratorIdentifier,
    TiramisuAction,
    TiramisuActionType,
)


class Reversal(TiramisuAction):
    """
    Reversal optimization command.
    """

    def __init__(self, iterator: IteratorIdentifier, tiramisu_tree: TiramisuTree):
        # Reversal takes one parameter of the loop to reverse
        self.iterator = tiramisu_tree.get_iterator_of_computation(
            iterator[0], iterator[1]
        )

        comps = tiramisu_tree.get_iterator_subtree_computations(self.iterator.name)
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        super().__init__(
            type=TiramisuActionType.REVERSAL, params=[self.iterator], comps=list(comps)
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        level = self.iterator.level
        for comp in self.comps:
            self.tiramisu_optim_str += f"{comp}.loop_reversal({level});\n"

        self.str_representation = f"R(L{level},comps={self.comps})"

        self.legality_check_string = self.tiramisu_optim_str

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
        if type(node.lower_bound) == int and type(node.upper_bound) == int:
            # Halide way of reversing to keep increment 1
            node.lower_bound, node.upper_bound = -node.upper_bound, -node.lower_bound
        else:
            node.lower_bound, node.upper_bound = node.upper_bound, node.lower_bound
