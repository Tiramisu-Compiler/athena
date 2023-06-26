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


class Tiling3D(TiramisuAction):
    """
    3D Tiling optimization command.
    """

    def __init__(self, params: list, tiramisu_tree: TiramisuTree):
        # 3D Tiling takes six parameters:
        # 1. The first loop to tile
        # 2. The second loop to tile
        # 3. The third loop to tile
        # 4. The tile size for the first loop
        # 5. The tile size for the second loop
        # 6. The tile size for the third loop
        assert len(params) == 6

        comps = set()
        for node in params[:3]:
            comps.update(tiramisu_tree.get_iterator_subtree_computations(node))
        comps = list(comps)
        comps.sort(key=lambda x: tiramisu_tree.computations_absolute_order[x])

        super().__init__(type=TiramisuActionType.TILING_2D, params=params, comps=comps)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        self.tiramisu_optim_str = ""
        loop_levels_and_factors = [
            str(tiramisu_tree.iterators[param].level) if index < 3 else str(param)
            for index, param in enumerate(self.params)
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.tile({', '.join(loop_levels_and_factors)});\n"
            )
        self.str_representation = "T3(L{},L{},L{},{},{},{})".format(
            *loop_levels_and_factors
        )

    @classmethod
    def get_candidates(
        cls, program_tree: TiramisuTree
    ) -> Dict[str, List[Tuple[str, str, str]]]:
        candidates: Dict[str, List[Tuple[str, str, str]]] = {}

        candidate_sections = program_tree.get_candidate_sections()

        for root in candidate_sections:
            candidates[root] = []
            for section in candidate_sections[root]:
                # Only consider sections with more than one iterator
                if len(section) > 2:
                    # Get all possible combinations of 3 successive iterators
                    successive_3_iterators = [
                        tuple(section[i : i + 3]) for i in range(len(section) - 2)
                    ]
                    candidates[root].extend(successive_3_iterators)

        return candidates

    def transform_tree(self, program_tree: TiramisuTree):
        node_1_outer = program_tree.iterators[self.params[0]]
        node_2_outer = program_tree.iterators[self.params[1]]
        node_3_outer = program_tree.iterators[self.params[2]]

        assert (
            type(node_1_outer.lower_bound) is int
            and type(node_1_outer.upper_bound) is int
        )
        assert (
            type(node_2_outer.lower_bound) is int
            and type(node_2_outer.upper_bound) is int
        )
        assert (
            type(node_3_outer.lower_bound) is int
            and type(node_3_outer.upper_bound) is int
        )

        extent_1 = node_1_outer.upper_bound - node_1_outer.lower_bound
        extent_2 = node_2_outer.upper_bound - node_2_outer.lower_bound
        extent_3 = node_3_outer.upper_bound - node_3_outer.lower_bound

        node_1_tiling_factor = self.params[3]
        node_2_tiling_factor = self.params[4]
        node_3_tiling_factor = self.params[5]

        # Create the first tiled node
        if extent_1 % node_1_tiling_factor == 0:
            tiled_1_upper_bound = node_1_tiling_factor
        else:
            tiled_1_upper_bound = f"({extent_1} - max({node_1_outer.name}*{node_1_tiling_factor}, {extent_1 - node_1_tiling_factor}))"

        node_1_inner = IteratorNode(
            name=f"{node_1_outer.name}_tiled",
            parent_iterator=node_3_outer.name,
            lower_bound=0,
            upper_bound=tiled_1_upper_bound,
            level=node_3_outer.level + 1,
            child_iterators=[f"{node_2_outer.name}_tiled"],
            computations_list=[],
        )

        # Create the second tiled node
        if extent_2 % node_2_tiling_factor == 0:
            tiled_2_upper_bound = node_2_tiling_factor
        else:
            tiled_2_upper_bound = f"({extent_2} - max({node_2_outer.name}*{node_2_tiling_factor}, {extent_2 - node_2_tiling_factor}))"

        node_2_inner = IteratorNode(
            name=f"{node_2_outer.name}_tiled",
            parent_iterator=node_1_inner.name,
            lower_bound=0,
            upper_bound=tiled_2_upper_bound,
            level=node_1_inner.level + 1,
            child_iterators=[f"{node_3_outer.name}_tiled"],
            computations_list=[],
        )

        # Create the third tiled node
        if extent_3 % node_3_tiling_factor == 0:
            tiled_3_upper_bound = node_3_tiling_factor
        else:
            tiled_3_upper_bound = f"({extent_3} - max({node_3_outer.name}*{node_3_tiling_factor}, {extent_3 - node_3_tiling_factor}))"

        node_3_inner = IteratorNode(
            name=f"{node_3_outer.name}_tiled",
            parent_iterator=node_2_inner.name,
            lower_bound=0,
            upper_bound=tiled_3_upper_bound,
            level=node_2_inner.level + 1,
            child_iterators=node_3_outer.child_iterators.copy(),
            computations_list=node_3_outer.computations_list.copy(),
        )

        # Update the children of the outer node 2
        for child in node_3_outer.child_iterators:
            program_tree.iterators[child].parent_iterator = node_3_inner.name

        # update node_1
        node_1_outer.upper_bound = math.ceil(extent_1 / node_1_tiling_factor)
        node_1_outer.lower_bound = 0

        # update node_2
        node_2_outer.upper_bound = math.ceil(extent_2 / node_2_tiling_factor)
        node_2_outer.lower_bound = 0

        # update node_3
        node_3_outer.upper_bound = math.ceil(extent_3 / node_3_tiling_factor)
        node_3_outer.lower_bound = 0
        node_3_outer.child_iterators = [node_1_inner.name]
        node_3_outer.computations_list = []

        # Update the level of the other iterators
        for iterator in program_tree.iterators.values():
            if iterator.level > node_3_outer.level:
                iterator.level += 3

        # Add the new nodes to the tree
        program_tree.iterators[node_1_inner.name] = node_1_inner
        program_tree.iterators[node_2_inner.name] = node_2_inner
        program_tree.iterators[node_3_inner.name] = node_3_inner

    def verify_conditions(self, tiramisu_tree: TiramisuTree) -> None:
        node_1 = tiramisu_tree.iterators[self.params[0]]
        node_2 = tiramisu_tree.iterators[self.params[1]]
        node_3 = tiramisu_tree.iterators[self.params[2]]
        node_1_tiling_factor = self.params[3]
        node_2_tiling_factor = self.params[4]
        node_3_tiling_factor = self.params[5]

        # Check that the two nodes are successive
        assert (
            node_2.parent_iterator == node_1.name
        ), f"Nodes {node_1.name} and {node_2.name} are not successive, parent of {node_2.name} is {node_2.parent_iterator} instead of {node_1.name}"
        assert (
            node_3.parent_iterator == node_2.name
        ), f"Nodes {node_2.name} and {node_3.name} are not successive, parent of {node_3.name} is {node_3.parent_iterator} instead of {node_2.name}"

        # assert that the bounds are integers
        assert (
            type(node_1.lower_bound) is int and type(node_1.upper_bound) is int
        ), f"Node {node_1.name} has non-integer bounds, lower bound: {node_1.lower_bound}, upper bound: {node_1.upper_bound}"
        assert (
            type(node_2.lower_bound) is int and type(node_2.upper_bound) is int
        ), f"Node {node_2.name} has non-integer bounds, lower bound: {node_2.lower_bound}, upper bound: {node_2.upper_bound}"
        assert (
            type(node_3.lower_bound) is int and type(node_3.upper_bound) is int
        ), f"Node {node_3.name} has non-integer bounds, lower bound: {node_3.lower_bound}, upper bound: {node_3.upper_bound}"

        # check that the tiling factors are positive and smaller than the extent of the node
        assert (
            node_1_tiling_factor > 0
        ), f"Tiling factor must be positive, got {node_1_tiling_factor}"
        assert (
            node_2_tiling_factor > 0
        ), f"Tiling factor must be positive, got {node_2_tiling_factor}"
        assert (
            node_3_tiling_factor > 0
        ), f"Tiling factor must be positive, got {node_3_tiling_factor}"

        assert (
            node_1_tiling_factor < node_1.upper_bound - node_1.lower_bound
        ), f"Tiling factor must be smaller than the extent of the node: {node_1_tiling_factor} < {node_1.upper_bound - node_1.lower_bound}"
        assert (
            node_2_tiling_factor < node_2.upper_bound - node_2.lower_bound
        ), f"Tiling factor must be smaller than the extent of the node: {node_2_tiling_factor} < {node_2.upper_bound - node_2.lower_bound}"
        assert (
            node_3_tiling_factor < node_3.upper_bound - node_3.lower_bound
        ), f"Tiling factor must be smaller than the extent of the node: {node_3_tiling_factor} < {node_3.upper_bound - node_3.lower_bound}"

        # check that the first 2 nodes do not have any computations
        assert (
            len(node_1.computations_list) == 0
        ), f"The first node must not have any computations: {node_1.name} has {node_1.computations_list}"
        assert (
            len(node_2.computations_list) == 0
        ), f"The second node must not have any computations: {node_2.name} has {node_2.computations_list}"

        # check that the first node has no child iterators besides the second node
        assert (
            len(node_1.child_iterators) == 1
            and node_1.child_iterators[0] == node_2.name
        ), f"The first node must have one child which is the second node but has {node_1.child_iterators}"

        # check that the second node has no child iterators besides the third node
        assert (
            len(node_2.child_iterators) == 1
            and node_2.child_iterators[0] == node_3.name
        ), f"The second node must have one child which is the third node but has {node_2.child_iterators}"
