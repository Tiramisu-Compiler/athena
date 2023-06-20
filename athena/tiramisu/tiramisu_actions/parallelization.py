from __future__ import annotations

from typing import Dict, TYPE_CHECKING, List

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Parallelization(TiramisuAction):
    """
    Parallelization optimization command.
    """

    def __init__(self, params: list, comps: list):
        # Prallelization only takes one parameter the loop to parallelize
        assert len(params) == 1
        assert len(comps) > 0

        super().__init__(
            type=TiramisuActionType.PARALLELIZATION, params=params, comps=comps
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        level = tiramisu_tree.iterators[self.params[0]].level
        self.tiramisu_optim_str = f"\n\t{self.comps[0]}.tag_parallel_level({level});"

        self.str_representation = "P(L" + str(level) + ")"

    @classmethod
    def _get_candidates_of_node(
        cls, node_name: str, program_tree: TiramisuTree
    ) -> list:
        candidates = []
        node = program_tree.iterators[node_name]

        if node.child_iterators:
            candidates.append(node.child_iterators)

            for child in node.child_iterators:
                candidates += cls._get_candidates_of_node(child, program_tree)

        return candidates

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> Dict[str, List[str]]:
        """Get the list of candidates for parallelization.

        Parameters:
        ----------
        `program_tree`: `TiramisuTree`
            The Tiramisu tree of the program.

        Returns:
        -------
        `Dict`
            Dictionary of candidates for parallelization of each root.
        """

        candidates = {}

        for root in program_tree.roots:
            candidates[root] = [[root]] + cls._get_candidates_of_node(
                root, program_tree
            )

        return candidates
