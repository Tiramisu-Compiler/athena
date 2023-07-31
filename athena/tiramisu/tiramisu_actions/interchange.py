from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING, Dict, List, Tuple

from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree

from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    CannotApplyException,
    IteratorIdentifier,
    TiramisuAction,
    TiramisuActionType,
)


class Interchange(TiramisuAction):
    """
    Interchange optimization command.
    """

    def __init__(self, params: List[IteratorIdentifier], tiramisu_tree: TiramisuTree):
        # Interchange takes 2 iterators to interchange as parameters
        assert len(params) == 2

        if isinstance(params[0], str):
            self.first_iterator = tiramisu_tree.iterators[params[0]]
        else:
            self.first_iterator = tiramisu_tree.get_iterator_of_computation(
                params[0][0], params[0][1]
            )

        if isinstance(params[1], str):
            self.second_iterator = tiramisu_tree.iterators[params[1]]
        else:
            self.second_iterator = tiramisu_tree.get_iterator_of_computation(
                params[1][0], params[1][1]
            )

        comps = tiramisu_tree.get_iterator_subtree_computations(
            self.first_iterator.name
        )
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        params = [self.first_iterator, self.second_iterator]

        super().__init__(
            type=TiramisuActionType.INTERCHANGE, params=params, comps=comps
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        levels = [param.level for param in self.params]
        for comp in self.comps:
            self.tiramisu_optim_str += f"{comp}.interchange({levels[0]},{levels[1]});\n"
        self.str_representation = f"I(L{levels[0]},L{levels[1]},comps={self.comps})"

        self.legality_check_string = self.tiramisu_optim_str

    @classmethod
    def get_candidates(
        cls, program_tree: TiramisuTree
    ) -> Dict[str, List[Tuple[str, str]]]:
        candidates: Dict[str, List[Tuple[str, str]]] = {}

        candidate_sections = program_tree.get_candidate_sections()

        for root in candidate_sections:
            candidates[root] = []
            for section in candidate_sections[root]:
                # Only consider sections with more than one iterator
                if len(section) > 1:
                    # Get all possible combinations of 2 iterators
                    candidates[root].extend(list(itertools.combinations(section, 2)))

        return candidates
