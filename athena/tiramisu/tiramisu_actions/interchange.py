from __future__ import annotations
import itertools
import re

from typing import Dict, TYPE_CHECKING, List, Tuple

from athena.tiramisu.tiramisu_iterator_node import IteratorNode
from athena.tiramisu.tiramisu_tree import TiramisuTree

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

    def __init__(self, params: list, tiramisu_tree: TiramisuTree):
        # Interchange only takes two parameters of the 2 loops to interchange
        assert len(params) == 2

        comps = tiramisu_tree.get_iterator_subtree_computations(params[0])
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        super().__init__(
            type=TiramisuActionType.INTERCHANGE, params=params, comps=comps
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        levels = [tiramisu_tree.iterators[param].level for param in self.params]
        for comp in self.comps:
            self.tiramisu_optim_str += f"{comp}.interchange({levels[0]},{levels[1]});\n"
        self.str_representation = (
            f"I(L{self.params[0]},L{self.params[1]},comps={self.comps})"
        )

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
                    # Get all possible combinations of 2 iterators
                    candidates[root].extend(list(itertools.combinations(section, 2)))

        return candidates

    def transform_tree(self, program_tree: TiramisuTree):
        # Get the iterators to interchange
        node1, node2 = self.params[0], self.params[1]

        # Get the iterators' parents
        node1_parent = program_tree.iterators[node1].parent_iterator
        node2_parent = program_tree.iterators[node2].parent_iterator

        # treat case where one iterator is the parent of the other
        if node2_parent == node1:
            new_node1_parent = node2
        else:
            new_node1_parent = node2_parent

        # Create the new iterators
        new_node1 = IteratorNode(
            name=node1,
            parent_iterator=new_node1_parent,
            lower_bound=program_tree.iterators[node1].lower_bound,
            upper_bound=program_tree.iterators[node1].upper_bound,
            child_iterators=program_tree.iterators[node2].child_iterators,
            computations_list=program_tree.iterators[node2].computations_list,
            level=program_tree.iterators[node2].level,
        )

        # treat case where one iterator is the parent of the other
        if node1_parent == node2:
            new_node2_parent = node1
        else:
            new_node2_parent = node1_parent

        # Create the new iterators
        new_node2 = IteratorNode(
            name=node2,
            parent_iterator=new_node2_parent,
            lower_bound=program_tree.iterators[node2].lower_bound,
            upper_bound=program_tree.iterators[node2].upper_bound,
            child_iterators=program_tree.iterators[node1].child_iterators,
            computations_list=program_tree.iterators[node1].computations_list,
            level=program_tree.iterators[node1].level,
        )

        # Update the iterators' parents
        if node1_parent:
            if node1_parent == node2:
                new_node1.child_iterators = [
                    node2 if x == node1 else x for x in new_node1.child_iterators
                ]
            else:
                parent_node = program_tree.iterators[node1_parent]  # type: ignore

                parent_node.child_iterators[
                    parent_node.child_iterators.index(node1)
                ] = node2
        else:
            program_tree.roots[program_tree.roots.index(node1)] = node2

        if node2_parent:
            if node2_parent == node1:
                new_node2.child_iterators = [
                    node1 if x == node2 else x for x in new_node2.child_iterators
                ]

            else:
                parent_node = program_tree.iterators[node2_parent]  # type: ignore

                parent_node.child_iterators[
                    parent_node.child_iterators.index(node2)
                ] = node1
        else:
            program_tree.roots[program_tree.roots.index(node2)] = node1

        # Update the iterators' children
        for child in program_tree.iterators[node1].child_iterators:
            program_tree.iterators[child].parent_iterator = node2

        for child in program_tree.iterators[node2].child_iterators:
            program_tree.iterators[child].parent_iterator = node1

        # swap the iterators
        program_tree.iterators[node1] = new_node1
        program_tree.iterators[node2] = new_node2

    def verify_conditions(self, tiramisu_tree: TiramisuTree) -> None:
        node_1 = tiramisu_tree.iterators[self.params[0]]
        node_2 = tiramisu_tree.iterators[self.params[1]]

        # order the nodes by level
        if node_1.level > node_2.level:
            node_1, node_2 = node_2, node_1

        if node_1.has_unkown_bounds() or node_2.has_unkown_bounds():
            raise Exception(
                "Interchange optimization cannot be applied to iterators with unknown bounds"
            )

        node_to_test = node_2
        while node_to_test.name != node_1.name:
            # check that node1.name is not node2 bounds using regex ending with \W
            if type(node_to_test.lower_bound) is str and re.search(
                rf"{node_1.name}\W", node_to_test.lower_bound
            ):
                raise Exception(
                    f"Cannot interchange {node_1.name} and {node_2.name} because {node_to_test.name} depends on {node_1.name}"
                )
            if type(node_to_test.upper_bound) is str and re.search(
                rf"{node_1.name}\W", node_to_test.upper_bound
            ):
                raise Exception(
                    f"Cannot interchange {node_1.name} and {node_2.name} because {node_to_test.name} depends on {node_1.name}"
                )
            if node_to_test.parent_iterator == None:
                break
            node_to_test = tiramisu_tree.iterators[node_to_test.parent_iterator]
