from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Tiling2D(TiramisuAction):
    """
    2D Tiling optimization command.
    """

    def __init__(self, params: list, comps: list):
        # 2D Tiling takes four parameters:
        # 1. The first loop to tile
        # 2. The second loop to tile
        # 3. The tile size for the first loop
        # 4. The tile size for the second loop
        assert len(params) == 4

        super().__init__(type=TiramisuActionType.TILING_2D, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_levels_and_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 2 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"\n\t{comp}.tile({', '.join(loop_levels_and_factors)});"
            )
        self.str_representation = "T2(L{},L{},{},{})".format(*loop_levels_and_factors)

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> Dict:
        candidates: Dict[str, List[Tuple[str, str]]] = {}

        candidate_sections = program_tree.get_candidate_sections()

        for root in candidate_sections:
            candidates[root] = []
            for section in candidate_sections[root]:
                # Only consider sections with more than one iterator
                if len(section) > 1:
                    # Get all possible combinations of 2 successive iterators
                    candidates[root].extend(list(itertools.pairwise(section)))

        return candidates
