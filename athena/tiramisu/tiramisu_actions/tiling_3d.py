from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Tiling3D(TiramisuAction):
    """
    3D Tiling optimization command.
    """

    def __init__(self, params: list, comps: list):
        # 3D Tiling takes six parameters:
        # 1. The first loop to tile
        # 2. The second loop to tile
        # 3. The third loop to tile
        # 4. The tile size for the first loop
        # 5. The tile size for the second loop
        # 6. The tile size for the third loop
        assert len(params) == 6

        super().__init__(type=TiramisuActionType.TILING_2D, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_levels_and_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 3 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.tile({', '.join(loop_levels_and_factors)});\n"
            )
        self.str_representation = "T3(L{},L{},L{},{},{},{})".format(
            *loop_levels_and_factors
        )

    @classmethod
    def get_candidates(
        cls, program_tree: TiramisuTree
    ) -> Dict[str, List[Tuple[str, str, str]]]:
        candidates: Dict[str, List[Tuple[str, str, str]]] = {}

        candidate_sections = program_tree.get_candidate_sections()

        for root in candidate_sections:
            candidates[root] = []
            for section in candidate_sections[root]:
                # Only consider sections with more than one iterator
                if len(section) > 2:
                    # Get all possible combinations of 3 successive iterators
                    successive_3_iterators = [
                        tuple(section[i : i + 3]) for i in range(len(section) - 2)
                    ]
                    candidates[root].extend(successive_3_iterators)

        return candidates
