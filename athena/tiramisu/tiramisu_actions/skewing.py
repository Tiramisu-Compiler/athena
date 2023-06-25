from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple
from athena.tiramisu.compiling_service import CompilingService
from athena.tiramisu.tiramisu_program import TiramisuProgram
from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
    from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Skewing(TiramisuAction):
    """
    Skewing optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Skewing  takes four parameters of the 2 loops to skew and their factors
        assert len(params) == 4
        assert len(comps) > 0

        super().__init__(type=TiramisuActionType.SKEWING, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        levels_with_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 2 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.skew({', '.join(levels_with_factors)});\n"
            )

        self.str_representation = f"S(L{levels_with_factors[0]},L{levels_with_factors[1]},{levels_with_factors[2]},{levels_with_factors[3]})"

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
                    # Get all possible combinations of 2 successive iterators
                    candidates[root].extend(list(itertools.pairwise(section)))
        return candidates

    @classmethod
    def get_factors(
        cls,
        schedule: Schedule,
        loop_levels: List[int],
        comps_skewed_loops: List[str],
    ) -> Tuple[int, int]:
        factors = CompilingService.call_skewing_solver(
            schedule, loop_levels, comps_skewed_loops
        )
        if factors is not None:
            return factors
        else:
            raise ValueError("Skewing did not return any factors")

    def transform_tree(self, program_tree: TiramisuTree):
        node_1 = program_tree.iterators[self.params[0]]
        node_2 = program_tree.iterators[self.params[1]]
        # We set the lower and upper bounds to UNK because we do not know how the bounds will change. Halide will calculate the new bounds based on the transformed space of the iterations.
        node_1.lower_bound = "UNK"
        node_1.upper_bound = "UNK"

        node_2.lower_bound = "UNK"
        node_2.upper_bound = "UNK"
