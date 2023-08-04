from __future__ import annotations

import copy
import itertools
import math
from typing import TYPE_CHECKING, Dict, List, Tuple

from athena.tiramisu.tiramisu_iterator_node import IteratorIdentifier
from athena.tiramisu.tiramisu_tree import TiramisuTree

if TYPE_CHECKING:
    from athena.tiramisu.tiramisu_tree import TiramisuTree

from athena.tiramisu.tiramisu_actions.tiramisu_action import (
    TiramisuAction,
    TiramisuActionType,
)


class Tiling3D(TiramisuAction):
    """
    3D Tiling optimization command.
    """

    def __init__(
        self,
        params: List[IteratorIdentifier | int],
        comps: List[str] | None = None,
    ):
        # 3D Tiling takes six parameters divided into three tuples:
        # 1. The first iterator to tile
        # 2. The second iterator to tile
        # 3. The third iterator to tile
        # 4. The tile size for the first iterator
        # 5. The tile size for the second iterator
        # 6. The tile size for the third iterator

        assert len(params) == 6
        assert (
            isinstance(params[0], tuple)
            and isinstance(params[1], tuple)
            and isinstance(params[2], tuple)
        )
        assert (
            isinstance(params[3], int)
            and isinstance(params[4], int)
            and isinstance(params[5], int)
        )

        self.params = params
        self.comps = comps

        self.iterators = [params[0], params[1], params[2]]
        self.tile_sizes = [params[3], params[4], params[5]]

        super().__init__(type=TiramisuActionType.TILING_3D, params=params, comps=comps)

    def initialize_action_for_tree(self, tiramisu_tree: TiramisuTree):
        # clone the tree to be able to restore it later
        self.tree = copy.deepcopy(tiramisu_tree)

        if self.comps is None:
            outermost_iterator_id = self.iterators[0]
            for iterator in self.iterators[1:]:
                if iterator[1] < outermost_iterator_id[1]:
                    outermost_iterator_id = iterator

            outermost_iterator = self.tree.get_iterator_of_computation(
                *outermost_iterator_id
            )
            # get the computations of the outermost iterator to tile which include the computations of the other iterators
            self.comps = self.tree.get_iterator_subtree_computations(
                outermost_iterator.name
            )

            # sort the computations according to the absolute order
            self.comps.sort(
                key=lambda comp: self.tree.computations_absolute_order[comp]
            )

        self.set_string_representations(tiramisu_tree)

    def set_string_representations(self, tiramisu_tree: TiramisuTree):
        assert len(self.params) == 6
        assert self.iterators is not None
        assert self.comps is not None

        self.tiramisu_optim_str = ""
        loop_levels_and_factors = [
            str(self.iterators[0][1]),
            str(self.iterators[1][1]),
            str(self.iterators[2][1]),
            str(self.tile_sizes[0]),
            str(self.tile_sizes[1]),
            str(self.tile_sizes[2]),
        ]
        for comp in self.comps:
            self.tiramisu_optim_str += (
                f"{comp}.tile({', '.join(loop_levels_and_factors)});\n"
            )
        self.str_representation = "T3(L{},L{},L{},{},{},{},comps={})".format(
            *loop_levels_and_factors, self.comps
        )

        self.legality_check_string = self.tiramisu_optim_str

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
