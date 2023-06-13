from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple
from athena.tiramisu.compiling_service import CompilingService
from athena.tiramisu.tiramisu_program import TiramisuProgram

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Skewing(TiramisuAction):
    """
    Skewing optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Interchange  takes four parameters of the 2 loops to skew and their factors
        assert len(params) == 4

        super().__init__(type=TiramisuActionType.SKEWING, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        levels_with_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 2 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.skew({', '.join(levels_with_factors)});\n\t"
            )

        self.str_representation = f"S(L{levels_with_factors[0]},L{levels_with_factors[1]},{levels_with_factors[2]},{levels_with_factors[3]})"

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
                    candidates[root].extend(list(itertools.pairwise(section)))
        return candidates

    @classmethod
    def get_factors(
        cls,
        loops: List[str],
        current_schedule: List[TiramisuAction],
        tiramisu_program: TiramisuProgram,
    ) -> Tuple[int, int]:
        factors = CompilingService.call_skewing_solver(
            tiramisu_program,
            current_schedule,
            tiramisu_program.tree.get_iterator_levels(loops),
        )
        if factors is not None:
            return factors
        else:
            raise ValueError("Skewing did not return any factors")
