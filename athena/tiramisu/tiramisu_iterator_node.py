from typing import List


class IteratorNode:
    def __init__(
        self,
        name: str,
        parent_iterator: str = None,
        lower_bound: int = None,
        upper_bound: int = None,
        child_iterators: List[str] = [],
        computations_list: List[str] = [],
    ):
        self.name = name
        self.parent_iterator = parent_iterator
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.child_iterators = child_iterators
        self.computations_list = computations_list

    def add_child(self, child: str) -> None:
        self.child_iterators.append(child)

    def add_computation(self, comp: str) -> None:
        self.computations_list.append(comp)

    def __str__(self) -> str:
        return f"{self.name}(lower_bound={self.lower_bound}, upper_bound={self.upper_bound}, child_iterators={self.child_iterators}, computations_list={self.computations_list})"

    def __repr__(self) -> str:
        return self.__str__()
