from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree

from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuAction,
    TiramisuActionType,
)


class Parallelization(TiramisuAction):
    """
    Parallelization optimization command.
    """

    def __init__(
        self,
        iterator_to_parallelize: str | Tuple[str, int],
        tiramisu_tree: TiramisuTree,
    ):
        # Parallelization only takes one parameter the loop to parallelize it can be the name of the iterator or a tuple (computation_name, iterator_level)
        self.loop_to_parallelize = iterator_to_parallelize
        if isinstance(iterator_to_parallelize, str):
            self.iterator = tiramisu_tree.iterators[iterator_to_parallelize]
        else:
            computation_name, iterator_level = iterator_to_parallelize

            assert iterator_level >= 0, "Iterator level must be positive"

            self.iterator = tiramisu_tree.get_iterator_of_computation(
                computation_name, iterator_level
            )

        comps = tiramisu_tree.get_iterator_subtree_computations(self.iterator.name)
        comps.sort(key=lambda comp: tiramisu_tree.computations_absolute_order[comp])

        super().__init__(
            type=TiramisuActionType.PARALLELIZATION,
            params=[self.iterator.name],
            comps=comps,
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        level = self.iterator.level
        first_comp = list(self.comps)[0]
        self.tiramisu_optim_str = f"{first_comp}.tag_parallel_level({level});\n"

        self.str_representation = f"P(L{level},comps={self.comps})"

        self.legality_check_string = f"is_legal &= loop_parallelization_is_legal({level}, {{{', '.join([f'&{comp}' for comp in self.comps]) }}});\n    {self.tiramisu_optim_str}"

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

    def transform_tree(self, program_tree: TiramisuTree):
        pass
