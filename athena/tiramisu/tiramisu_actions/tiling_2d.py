from __future__ import annotations
import itertools
import math

from typing import Dict, TYPE_CHECKING, List, Tuple
from athena.tiramisu.tiramisu_iterator_node import IteratorNode

from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree
from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuActionType,
    TiramisuAction,
)


class Tiling2D(TiramisuAction):
    """
    2D Tiling optimization command.
    """

    def __init__(self, params: list, tiramisu_tree: TiramisuTree):
        # 2D Tiling takes four parameters:
        # 1. The first loop to tile
        # 2. The second loop to tile
        # 3. The tile size for the first loop
        # 4. The tile size for the second loop
        assert len(params) == 4

        comps = set()
        for node in params[:2]:
            comps.update(tiramisu_tree.get_iterator_subtree_computations(node))
        comps = list(comps)
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        super().__init__(type=TiramisuActionType.TILING_2D, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_levels_and_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 2 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.tile({', '.join(loop_levels_and_factors)});\n"
            )
        self.str_representation = "T2(L{},L{},{},{})".format(*loop_levels_and_factors)

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

    def transform_tree(self, program_tree: TiramisuTree):
        node_1_outer = program_tree.iterators[self.params[0]]
        node_2_outer = program_tree.iterators[self.params[1]]
        node_1_tiling_factor = self.params[2]
        node_2_tiling_factor = self.params[3]

        if node_1_outer.has_integer_bounds():
            assert (
                type(node_1_outer.lower_bound) is int
                and type(node_1_outer.upper_bound) is int
            )
            extent_1 = node_1_outer.upper_bound - node_1_outer.lower_bound

            # Create the first tiled node
            if extent_1 % node_1_tiling_factor == 0:
                tiled_1_upper_bound = node_1_tiling_factor
            else:
                tiled_1_upper_bound = f"({extent_1} - max({node_1_outer.name}*{node_1_tiling_factor}, {extent_1 - node_1_tiling_factor}))"
            node_1_outer_upper_bound = math.ceil(extent_1 / node_1_tiling_factor)
        else:
            tiled_1_upper_bound = "UNK"
            node_1_outer_upper_bound = "UNK"

        node_1_inner = IteratorNode(
            name=f"{node_1_outer.name}_tiled",
            parent_iterator=node_2_outer.name,
            lower_bound=0,
            upper_bound=tiled_1_upper_bound,
            level=node_2_outer.level + 1,
            child_iterators=[f"{node_2_outer.name}_tiled"],
            computations_list=[],
        )

        if node_2_outer.has_integer_bounds():
            assert (
                type(node_2_outer.lower_bound) is int
                and type(node_2_outer.upper_bound) is int
            )
            # Create the second tiled node
            extent_2 = node_2_outer.upper_bound - node_2_outer.lower_bound
            if extent_2 % node_2_tiling_factor == 0:
                tiled_2_upper_bound = node_2_tiling_factor
            else:
                tiled_2_upper_bound = f"({extent_2} - max({node_2_outer.name}*{node_2_tiling_factor}, {extent_2 - node_2_tiling_factor}))"
            node_2_outer_upper_bound = math.ceil(extent_2 / node_2_tiling_factor)
        else:
            tiled_2_upper_bound = "UNK"
            node_2_outer_upper_bound = "UNK"

        node_2_inner = IteratorNode(
            name=f"{node_2_outer.name}_tiled",
            parent_iterator=node_1_inner.name,
            lower_bound=0,
            upper_bound=tiled_2_upper_bound,
            level=node_1_inner.level + 1,
            child_iterators=node_2_outer.child_iterators.copy(),
            computations_list=node_2_outer.computations_list.copy(),
        )

        # Update the children of the outer node 2
        for child in node_2_outer.child_iterators:
            program_tree.iterators[child].parent_iterator = node_2_inner.name

        # update node_1
        node_1_outer.upper_bound = node_1_outer_upper_bound
        node_1_outer.lower_bound = 0

        # update node_2
        node_2_outer.upper_bound = node_2_outer_upper_bound
        node_2_outer.lower_bound = 0
        node_2_outer.child_iterators = [node_1_inner.name]
        node_2_outer.computations_list = []

        # Update the level of the other iterators
        for iterator in program_tree.iterators.values():
            if iterator.level > node_2_outer.level:
                iterator.level += 2

        # Add the new nodes to the tree
        program_tree.iterators[node_1_inner.name] = node_1_inner
        program_tree.iterators[node_2_inner.name] = node_2_inner

    def verify_conditions(self, tiramisu_tree: TiramisuTree) -> None:
        node_1 = tiramisu_tree.iterators[self.params[0]]
        node_2 = tiramisu_tree.iterators[self.params[1]]
        node_1_tiling_factor = self.params[2]
        node_2_tiling_factor = self.params[3]

        # Check that the two nodes are successive
        assert (
            node_2.parent_iterator == node_1.name
        ), f"Nodes {node_1.name} and {node_2.name} are not successive, parent of {node_2.name} is {node_2.parent_iterator} instead of {node_1.name}"

        # assert that the bounds are integers
        # assert (
        #     type(node_1.lower_bound) is int and type(node_1.upper_bound) is int
        # ), f"Node {node_1.name} has non-integer bounds, lower bound: {node_1.lower_bound}, upper bound: {node_1.upper_bound}"
        # assert (
        #     type(node_2.lower_bound) is int and type(node_2.upper_bound) is int
        # ), f"Node {node_2.name} has non-integer bounds, lower bound: {node_2.lower_bound}, upper bound: {node_2.upper_bound}"

        # check that the tiling factors are positive and smaller than the extent of the node
        assert (
            node_1_tiling_factor > 0
        ), f"Tiling factor must be positive, got {node_1_tiling_factor}"
        assert (
            node_2_tiling_factor > 0
        ), f"Tiling factor must be positive, got {node_2_tiling_factor}"

        if node_1.has_integer_bounds():
            assert type(node_1.lower_bound) is int and type(node_1.upper_bound) is int
            assert (
                node_1_tiling_factor < node_1.upper_bound - node_1.lower_bound
            ), f"Tiling factor must be smaller than the extent of the node: {node_1_tiling_factor} < {node_1.upper_bound - node_1.lower_bound}"
        if node_2.has_integer_bounds():
            assert type(node_2.lower_bound) is int and type(node_2.upper_bound) is int
            assert (
                node_2_tiling_factor < node_2.upper_bound - node_2.lower_bound
            ), f"Tiling factor must be smaller than the extent of the node: {node_2_tiling_factor} < {node_2.upper_bound - node_2.lower_bound}"

        # check that the first node does not have any computations
        assert (
            len(node_1.computations_list) == 0
        ), f"The first node must not have any computations: {node_1.name} has {node_1.computations_list}"

        # check that the first node has no child iterators besides the second node
        assert (
            len(node_1.child_iterators) == 1
            and node_1.child_iterators[0] == node_2.name
        ), f"The first node must have one child which is the second node but has {node_1.child_iterators}"
