from __future__ import annotations

from typing import Dict, TYPE_CHECKING, List

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    CannotApplyException,
    TiramisuActionType,
    TiramisuAction,
)


class Parallelization(TiramisuAction):
    """
    Parallelization optimization command.
    """

    def __init__(self, params: list, tiramisu_tree: TiramisuTree):
        # Parallelization only takes one parameter the loop to parallelize
        assert len(params) == 1

        comps = tiramisu_tree.get_iterator_subtree_computations(params[0])
        comps.sort(key=lambda comp: tiramisu_tree.computations_absolute_order[comp])

        super().__init__(
            type=TiramisuActionType.PARALLELIZATION, params=params, comps=comps
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        level = tiramisu_tree.iterators[self.params[0]].level
        first_comp = list(self.comps)[0]
        self.tiramisu_optim_str = f"{first_comp}.tag_parallel_level({level});\n"

        self.str_representation = f"P(L{level},comps={self.comps})"

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

    def legality_check_string(self, program_tree: TiramisuTree) -> str:
        """Return the tiramisu code that checks the legality of the optimization command."""
        if self.tiramisu_optim_str == "":
            raise ValueError(
                "The legality check should be called after the optimization string is set."
            )

        return f"is_legal &= loop_parallelization_is_legal({ program_tree.iterators[self.params[0]].level}, {{{', '.join([f'&{comp}' for comp in self.comps]) }}});\n    {self.tiramisu_optim_str}"

    def transform_tree(self, program_tree: TiramisuTree):
        pass

    def verify_conditions(self, program_tree: TiramisuTree, params=None):
        if params is None:
            params = self.params
        # Prallelization only takes one parameter the loop to parallelize
        if not len(params) == 1:
            raise CannotApplyException(
                f"Parallelization takes one parameter, {len(self.params)} given."
            )
