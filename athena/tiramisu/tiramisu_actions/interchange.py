from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Interchange(TiramisuAction):
    """
    Interchange optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Interchange only takes two parameters of the 2 loops to interchange
        assert len(params) == 2

        super().__init__(
            type=TiramisuActionType.INTERCHANGE, params=params, comps=comps
        )

    def get_tiramisu_optim_str(self, tiramisu_tree: TiramisuTree):
        tiramisu_optim_str = ""
        levels = [tiramisu_tree.iterators[param].level for param in self.params]
        for comp in self.comps:
            tiramisu_optim_str += f"{comp}.interchange({levels[0]},{levels[1]});\n\t"

        return tiramisu_optim_str

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> Dict:
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
