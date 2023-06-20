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
        self.tiramisu_optim_str = ""
        # get order of computations from the tree
        ordered_computations = tiramisu_tree.computations
        ordered_computations.sort(
            key=lambda x: tiramisu_tree.computations_absolute_order[x]
        )

        fusion_levels = self.get_fusion_levels(ordered_computations, tiramisu_tree)

        first_comp = ordered_computations[0]
        self.tiramisu_optim_str += f"""
    clear_implicit_function_sched_graph();
    {first_comp}{''.join([f'.then({comp},{fusion_level})' for comp, fusion_level in zip(ordered_computations[1:], fusion_levels)])};"""
        self.str_representation = f"F({','.join(self.comps)}, L{tiramisu_tree.iterators[self.params[0]].level})"

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

    def verify_conditions(self, program_tree: TiramisuTree):
        # assert that all the iterators have the same level
        assert (
            len(set([program_tree.iterators[param].level for param in self.params]))
            == 1
        )

        # assert that all the iterators have the same parent
        assert (
            len(
                set(
                    [
                        program_tree.iterators[param].parent_iterator
                        for param in self.params
                    ]
                )
            )
            == 1
        )

    def get_fusion_levels(self, computations: List[str], tiramisu_tree: TiramisuTree):
        fusion_levels = []
        # for every pair of successive computations get the shared iterator level
        for comp1, comp2 in itertools.pairwise(computations):
            # get the shared iterator level
            iter_comp_1 = tiramisu_tree.get_iterator_of_computation(comp1)
            iter_comp_2 = tiramisu_tree.get_iterator_of_computation(comp2)
            fusion_level = None

            # get the shared iterator level
            while iter_comp_1.name != iter_comp_2.name:
                if iter_comp_1.level > iter_comp_2.level:
                    # if parent is None then the iterators don't have a common parent
                    if iter_comp_1.parent_iterator is None:
                        fusion_level = -1
                        break
                    else:
                        iter_comp_1 = tiramisu_tree.iterators[
                            iter_comp_1.parent_iterator
                        ]
                else:
                    if iter_comp_2.parent_iterator is None:
                        fusion_level = -1
                        break
                    else:
                        iter_comp_2 = tiramisu_tree.iterators[
                            iter_comp_2.parent_iterator
                        ]

            if fusion_level is None:
                fusion_level = iter_comp_1.level

            fusion_levels.append(fusion_level)

        return fusion_levels
