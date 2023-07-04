from __future__ import annotations
import copy
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple
from athena.tiramisu.tiramisu_iterator_node import IteratorNode

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    CannotApplyException,
    TiramisuActionType,
    TiramisuAction,
)


class Unrolling(TiramisuAction):
    """
    Unrolling optimization command.
    """

    def __init__(self, params: list, tiramisu_tree: TiramisuTree):
        # Unrolling takes 2 parameters: the iterator to unroll and the unrolling factor
        assert len(params) == 2

        # check if node was renamed
        while (
            params[0] not in tiramisu_tree.iterators
            and params[0] in tiramisu_tree.renamed_iterators
        ):
            params[0] = tiramisu_tree.renamed_iterators[params[0]]

        comps = tiramisu_tree.get_iterator_subtree_computations(params[0])
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        super().__init__(type=TiramisuActionType.UNROLLING, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_level = tiramisu_tree.iterators[self.params[0]].level
        unrolling_factor = self.params[1]
        # for comp in self.comps:
        self.tiramisu_optim_str = "\n    ".join(
            [f"{comp}.unroll({loop_level},{unrolling_factor});" for comp in self.comps]
        )
        self.str_representation = (
            f"U(L{str(loop_level)},{str(unrolling_factor)},comps={self.comps})"
        )

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> List[str]:
        candidates: List[str] = []

        for iterator in program_tree.iterators:
            iterator_node = program_tree.iterators[iterator]
            if not iterator_node.child_iterators and iterator_node.computations_list:
                candidates.append(iterator)

        return candidates

    def legality_check_string(self, tiramisu_tree: TiramisuTree) -> str:
        """Return the tiramisu code that checks the legality of the optimization command."""
        if self.tiramisu_optim_str == "":
            raise CannotApplyException(
                "The legality check should be called after the optimization string is set."
            )

        level = tiramisu_tree.iterators[self.params[0]].level

        legality_check_str = f"is_legal &= loop_unrolling_is_legal({level}, {{{', '.join([f'&{comp}' for comp in self.comps])}}});\n"

        legality_check_str += f"    {self.tiramisu_optim_str}"

        return legality_check_str

    def transform_tree(self, program_tree: TiramisuTree):
        """Transform the tree according to the optimization command."""

        node = program_tree.iterators[self.params[0]]
        unroll_factor = self.params[1]

        if node.has_integer_bounds():
            assert type(node.lower_bound) is int and type(node.upper_bound) is int
            extent = node.upper_bound - node.lower_bound
            if unroll_factor == extent:
                return
            elif unroll_factor > extent:
                raise CannotApplyException(
                    "Unrolling factor cannot be greater than the extent of the loop."
                )
            elif extent % unroll_factor == 0:
                # Halide changes bounds to start from 0
                node.lower_bound = 0
                node.upper_bound = int(extent / unroll_factor)

                # Add the new iterators
                new_node = IteratorNode(
                    name=node.name + "_unroll",
                    parent_iterator=node.name,
                    lower_bound=0,
                    upper_bound=unroll_factor,
                    child_iterators=node.child_iterators.copy(),
                    computations_list=node.computations_list.copy(),
                    level=node.level + 1,
                )

                # update the parent iterator of the children
                for child in node.child_iterators:
                    program_tree.iterators[child].parent_iterator = new_node.name

                # change level of subtree
                children_to_change_level = node.child_iterators.copy()

                while children_to_change_level:
                    child = children_to_change_level.pop()
                    program_tree.iterators[child].level += 1
                    children_to_change_level.extend(
                        program_tree.iterators[child].child_iterators
                    )

                # Add the new iterators to the tree
                node.child_iterators = [new_node.name]
                node.computations_list = []

                program_tree.iterators[new_node.name] = new_node

            elif extent // unroll_factor == 1:
                cloned_subtree = program_tree.clone_subtree(node.name, "_unroll")

                cloned_root = cloned_subtree.roots[0]
                cloned_subtree.iterators[cloned_root].lower_bound = unroll_factor
                cloned_subtree.iterators[cloned_root].upper_bound = extent

                if node.parent_iterator is None:
                    program_tree.insert_subtree(
                        cloned_subtree, node.name, is_root_parent=True
                    )
                else:
                    program_tree.insert_subtree(cloned_subtree, node.parent_iterator)

                node.lower_bound = 0
                node.upper_bound = unroll_factor
            else:
                quotient = extent // unroll_factor

                cloned_subtree = program_tree.clone_subtree(node.name, "_unroll")

                cloned_root = cloned_subtree.roots[0]
                cloned_subtree.iterators[cloned_root].lower_bound = (
                    unroll_factor * quotient
                )
                cloned_subtree.iterators[cloned_root].upper_bound = extent

                if node.parent_iterator is None:
                    program_tree.insert_subtree(
                        cloned_subtree, node.name, is_root_parent=True
                    )
                else:
                    program_tree.insert_subtree(cloned_subtree, node.parent_iterator)

                node.lower_bound = 0
                node.upper_bound = quotient

                # Add the unrolling iterator under the node
                new_node = IteratorNode(
                    name=node.name + "_child_unroll",
                    parent_iterator=node.name,
                    lower_bound=0,
                    upper_bound=unroll_factor,
                    child_iterators=node.child_iterators.copy(),
                    computations_list=node.computations_list.copy(),
                    level=node.level + 1,
                )

                # update the parent iterator of the children
                for child in node.child_iterators:
                    program_tree.iterators[child].parent_iterator = new_node.name

                program_tree.iterators[new_node.name] = new_node

                # change level of subtree
                program_tree.update_subtree_levels(new_node.name, node.level + 1)

                node.child_iterators = [new_node.name]
                node.computations_list = []

        #         # Add the new iterators
        #         new_node = IteratorNode(
        #             name=node.name + "_unroll",
        #             parent_iterator=node.parent_iterator,
        #             lower_bound=extent - unroll_factor,
        #             upper_bound=extent,
        #             child_iterators=[
        #                 f"{child}_unroll" for child in node.child_iterators
        #             ],
        #             computations_list=[
        #                 f"{comp}_unroll" for comp in node.computations_list
        #             ],
        #             level=node.level,
        #         )

        #         nodes_to_clone = node.child_iterators.copy()

        #         while nodes_to_clone:
        #             child = nodes_to_clone.pop()
        #             child_node = program_tree.iterators[child]
        #             child_node_clone = copy.deepcopy(child_node)

        #             assert child_node_clone.parent_iterator

        #             child_node_clone.name = child_node_clone.name + "_unroll"
        #             child_node_clone.parent_iterator = (
        #                 child_node_clone.parent_iterator + "_unroll"
        #             )
        #             child_node_clone.computations_list = [
        #                 f"{comp}_unroll" for comp in child_node_clone.computations_list
        #             ]
        #             child_node_clone.child_iterators = [
        #                 f"{child}_unroll" for child in child_node_clone.child_iterators
        #             ]

        #             program_tree.iterators[child_node_clone.name] = child_node_clone
        #             program_tree.computations.extend(child_node_clone.computations_list)
        #             nodes_to_clone.extend(child_node.child_iterators)

        #         if new_node.parent_iterator is None:
        #             program_tree.roots.insert(
        #                 program_tree.roots.index(node.name) + 1, new_node.name
        #             )
        #         else:
        #             program_tree.iterators[
        #                 new_node.parent_iterator
        #             ].child_iterators.append(new_node.name)

        #         program_tree.iterators[new_node.name] = new_node

        #         node.lower_bound = 0
        #         node.upper_bound = extent // unroll_factor

    def verify_conditions(self, tiramisu_tree: TiramisuTree, params=None) -> None:
        if params is None:
            params = self.params
        # Unrolling only takes two parameters, the loop level and the factor
        if len(params) != 2:
            raise CannotApplyException(
                "Unrolling only takes two parameters, the loop level and the factor"
            )
