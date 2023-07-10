from __future__ import annotations
import itertools

from typing import Dict, TYPE_CHECKING, List, Tuple

from athena.tiramisu.tiramisu_iterator_node import IteratorNode

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    CannotApplyException,
    TiramisuActionType,
    TiramisuAction,
)


class Distribution(TiramisuAction):
    """
    Distribution optimization command.
    """

    def __init__(
        self,
        params: List[str],
        tiramisu_tree: TiramisuTree,
        children: List[List[str]] | None = None,
    ):
        # Distribution takes 1 parameters the iterator to be distributed
        assert len(params) == 1

        if children is None:
            children = []
            for comp in tiramisu_tree.iterators[params[0]].computations_list:
                children.append([comp])
            for child_iterator in tiramisu_tree.iterators[params[0]].child_iterators:
                children.append([child_iterator])

        super().__init__(
            type=TiramisuActionType.DISTRIBUTION, params=params, comps=children
        )

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        # get order of computations from the tree
        ordered_computations = tiramisu_tree.computations
        ordered_computations.sort(
            key=lambda x: tiramisu_tree.computations_absolute_order[x]
        )

        comps = []
        for comp_list in self.comps:
            comps.extend(comp_list)

        fusion_levels = self.get_fusion_levels(ordered_computations, tiramisu_tree)

        first_comp = ordered_computations[0]
        self.tiramisu_optim_str += f"clear_implicit_function_sched_graph();\n    {first_comp}{''.join([f'.then({comp},{fusion_level})' for comp, fusion_level in zip(ordered_computations[1:], fusion_levels)])};\n"
        self.str_representation = f"D(L{tiramisu_tree.iterators[self.params[0]].level},comps={comps},distribution={self.comps})"

        self.legality_check_string = self.tiramisu_optim_str

    @classmethod
    def get_candidates(cls, program_tree: TiramisuTree) -> List[str]:
        # We will try to distribute all the iterators with more than one computation
        candidates: List[str] = []

        for iterator in program_tree.iterators.values():
            if len(iterator.computations_list) + len(iterator.child_iterators) > 1:
                candidates.append(iterator.name)

        return candidates

    def verify_conditions(self, program_tree: TiramisuTree, params=None):
        if params is None:
            params = self.params

        # check if the node was renamed
        while (
            params[0] not in program_tree.iterators
            and params[0] in program_tree.renamed_iterators
        ):
            params[0] = program_tree.renamed_iterators[params[0]]

        try:
            assert len(params) == 1, "Distribution takes 1 parameter"
            assert (
                params[0] in program_tree.iterators
            ), f"iterator {params[0]} not found"
            assert (
                len(program_tree.iterators[params[0]].computations_list)
                + len(program_tree.iterators[params[0]].child_iterators)
                > 1
            ), f"iterator {params[0]} has only one or no computations/iterators to distribute"

            all_comps = []
            for comp_list in self.comps:
                assert type(comp_list) == list, "children list must be a list"
                all_comps += comp_list
            all_comps.sort()
            iterator_children = program_tree.iterators[params[0]].computations_list
            iterator_children.extend(program_tree.iterators[params[0]].child_iterators)
            iterator_children.sort()

            assert (
                all_comps == iterator_children
            ), f"children list {all_comps} does not match iterator computation + child_iterators lists {iterator_children}"

        except AssertionError as e:
            raise CannotApplyException(e.args)

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

    def transform_tree(self, program_tree: TiramisuTree):
        """
        Transform the tree by fusing the two iterators of the fusion command.

        Parameters
        ----------
        `program_tree` : `TiramisuTree`
            The tree to transform.
        """
        # get the iterators to fuse
        node_1_name = self.params[0]

        node_1 = program_tree.iterators[node_1_name]

        assert type(self.comps) == list and type(self.comps[0]) == list

        new_iterators = []
        for idx, list_comp in enumerate(self.comps):
            assert type(list_comp) == list
            new_node_name = f"{node_1_name}_dist_{idx}" if idx > 0 else node_1_name

            computations = [
                comp for comp in list_comp if comp in program_tree.computations
            ]

            iterators = []

            # filter the iterators
            for child in list_comp:
                if child in program_tree.iterators:
                    # add it to the list of child iterators of the new node
                    iterators.append(child)
                    # change the parent of the child iterator
                    program_tree.iterators[child].parent_iterator = new_node_name

            # create new iterator node
            new_iterator = IteratorNode(
                name=new_node_name,
                level=node_1.level,
                parent_iterator=node_1.parent_iterator,
                computations_list=computations,
                child_iterators=iterators,
                lower_bound=node_1.lower_bound,
                upper_bound=node_1.upper_bound,
            )

            new_iterators.append(new_iterator)

        # remove node_1 from the tree
        program_tree.iterators.pop(node_1_name)

        # add the new iterators to the tree
        for new_iterator in new_iterators:
            program_tree.iterators[new_iterator.name] = new_iterator

        # order the new iterators
        new_iterators.sort(
            key=lambda x: program_tree.computations_absolute_order[
                program_tree.get_iterator_subtree_computations(x.name)[0]
            ]
        )

        # update the node_1 parent
        if node_1.parent_iterator is not None:
            parent_node = program_tree.iterators[node_1.parent_iterator]
            parent_node.child_iterators.remove(node_1_name)
            parent_node.child_iterators.extend(
                [new_iterator.name for new_iterator in new_iterators]
            )
        else:
            program_tree.roots.remove(node_1_name)
            program_tree.roots.extend(
                [new_iterator.name for new_iterator in new_iterators]
            )
