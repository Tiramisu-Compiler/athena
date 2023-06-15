from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Fusion(TiramisuAction):
    """
    Fusion optimization command.
    """

    def __init__(self, params: List[str], comps: List[str]):
        # Fusion only takes the two names of the 2 iterators to fuse
        assert len(params) == 2

        super().__init__(type=TiramisuActionType.FUSION, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        # assert that all the iterators have the same level
        assert (
            len(set([tiramisu_tree.iterators[param].level for param in self.params]))
            == 1
        )

        # assert that all the iterators have the same parent
        assert (
            len(
                set(
                    [
                        tiramisu_tree.iterators[param].parent_iterator
                        for param in self.params
                    ]
                )
            )
            == 1
        )

        self.tiramisu_optim_str = ""
        levels = [tiramisu_tree.iterators[param].level for param in self.params]

        first_comp = self.comps[0]
        self.tiramisu_optim_str += f"\n\t{first_comp}{''.join([f'.then({comp},{levels[0]})' for comp in self.comps[1:]])};"
        self.str_representation = f"F({','.join(self.comps)})"

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> List[Tuple[str, str]]:
        # We will try to fuse all possible nodes that have the same level
        candidates: List[Tuple[str, str]] = []

        #  Check if roots are fusionable
        if len(program_tree.roots) > 1:
            # get all the possible combinations of 2 of roots
            candidates.extend(itertools.combinations(program_tree.roots, 2))

        # Check the different levels of the iterators
        levels = set([iterator.level for iterator in program_tree.iterators.values()])

        # For each level, we will try to fuse all possible nodes that have the same level and have the same root
        for level in levels:
            # get all iterator nodes that have the same level
            iterators = [
                iterator
                for iterator in program_tree.iterators.values()
                if iterator.level == level
            ]

            # filter the iterators that have the same root into dict
            iterators_dict: Dict[str, List[str]] = {}
            for root in program_tree.roots:
                iterators_dict[root] = []
            for iterator in iterators:
                iterators_dict[program_tree.get_root_of_node(iterator.name)].append(
                    iterator.name
                )
            for root in iterators_dict:
                candidates.extend(itertools.combinations(iterators_dict[root], 2))

        return candidates
