from typing import Dict, List, Tuple
from athena.tiramisu.tiramisu_iterator_node import IteratorNode
import itertools


class TiramisuTree:
    """This class represents the tree structure of a Tiramisu program.
    It is composed of a list of IteratorNode objects, each of which represents an iterator
    in the Tiramisu program. Each IteratorNode object contains information about its
    parent iterator, child iterators, lower and upper bounds, and the computations that
    it is associated with.

    Attributes:
    ----------
    `roots`: `List[str]`
        List of names of the root iterators in the Tiramisu program.
    `iterators`: `Dict[str, IteratorNode]`
        Dictionary of IteratorNode objects, indexed by the name of the iterator.
    `computations`: `List[str]`
        List of names of the computations in the Tiramisu program.

    Methods:
    -------
    `from_annotations(cls, annotations: Dict) -> "TiramisuTree":`
        Creates a TiramisuTree object from the annotations of a Tiramisu program.
    `get_candidate_sections(self) -> List[List[str]]:`
        Returns a list of candidate sections in the Tiramisu program.

    """

    def __init__(self) -> None:
        self.roots: List[str] = []
        self.iterators: Dict[str, IteratorNode] = {}
        self.computations: List[str] = []

    def add_root(self, root: str) -> None:
        self.roots.append(root)

    def add_computation(self, comp: str) -> None:
        self.computations.append(comp)

    @classmethod
    def from_annotations(cls, annotations: Dict) -> "TiramisuTree":
        """
        Creates a TiramisuTree object from the annotations of a Tiramisu program.

        Parameters:
        ----------
        `annotations`: `Dict`
            Annotations of a Tiramisu program.

        Returns:
        -------
        `tiramisu_space`: `TiramisuTree`
        """
        tiramisu_space = cls()

        iterators = annotations["iterators"]

        for iterator in iterators:
            if iterators[iterator]["parent_iterator"] is None:
                tiramisu_space.add_root(iterator)

            tiramisu_space.iterators[iterator] = IteratorNode(
                name=iterator,
                lower_bound=iterators[iterator]["lower_bound"],
                upper_bound=iterators[iterator]["upper_bound"],
                child_iterators=iterators[iterator]["child_iterators"],
                computations_list=iterators[iterator]["computations_list"],
                parent_iterator=iterators[iterator]["parent_iterator"],
            )
            tiramisu_space.computations.extend(iterators[iterator]["computations_list"])

        return tiramisu_space

    def __str__(self) -> str:
        return f"Roots: {self.roots}\nComputations: {self.computations}\nIterators: {self.iterators}"

    def __repr__(self) -> str:
        return self.__str__()

    def get_candidate_sections(self) -> List[List[str]]:
        """
        Returns a list of candidate sections, also named Branches by the team, where transformations can potentially be applied in the Tiramisu program.

        Returns:
        -------
        `list_candidate_sections`: `List[List[str]]`
            List of candidate sections in the Tiramisu program.
        """
        nodes_to_visit = self.roots.copy()
        list_candidate_sections = []
        for node in nodes_to_visit:
            candidate_section, new_nodes_to_visit = self._get_section_of_node(node)
            list_candidate_sections.append(candidate_section)
            nodes_to_visit.extend(new_nodes_to_visit)
        return list_candidate_sections

    def _get_section_of_node(self, node_name: str) -> Tuple[List[str], List[str]]:
        candidate_section = [node_name]
        current_node = self.iterators[node_name]

        while (
            len(current_node.child_iterators) == 1
            and len(current_node.computations_list) == 0
        ):
            next_node_name = current_node.child_iterators[0]
            candidate_section.append(next_node_name)
            current_node = self.iterators[next_node_name]

        if current_node.child_iterators:
            return candidate_section, current_node.child_iterators
        return candidate_section, []

    def get_level_of_node(self, node_name: str) -> int:
        """
        Returns the level of the node in the program tree.

        Parameters:
        ----------
        `node_name`: `str`
            The name of the node.

        `program_tree`: `TiramisuTree`
            The Tiramisu tree of the program.

        Returns:
        -------
        int
            The level of the node.
        """

        node = self.iterators[node_name]
        level = 0

        while node.parent_iterator:
            level += 1
            node = self.iterators[node.parent_iterator]

        return level
