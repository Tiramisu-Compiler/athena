from __future__ import annotations
from copy import deepcopy
import re

from typing import List, TYPE_CHECKING
from athena.tiramisu.compiling_service import CompilingService
from athena.tiramisu.tiramisu_actions.tiramisu_action import TiramisuActionType

if TYPE_CHECKING:
    from .tiramisu_actions.tiramisu_action import TiramisuAction
from athena.tiramisu.tiramisu_program import TiramisuProgram
from athena.tiramisu import tiramisu_actions


class Schedule:
    """
    A schedule is a list of optimizations to be applied to a Tiramisu program.

    Parameters
    ----------
    `tiramisu_program` : TiramisuProgram
        The Tiramisu program to which the schedule will be applied.
    `optims_list` : List[TiramisuAction]
        The list of optimizations to be applied to the Tiramisu program.
    """

    def __init__(self, tiramisu_program: TiramisuProgram | None = None) -> None:
        self.tiramisu_program = tiramisu_program
        self.optims_list: List[TiramisuAction] = []
        if tiramisu_program:
            self.tree = deepcopy(tiramisu_program.tree)
        else:
            self.tree = None
        self.legality: bool | None = None

    def set_tiramisu_program(self, tiramisu_program: TiramisuProgram) -> None:
        self.tiramisu_program = tiramisu_program
        self.tree = deepcopy(tiramisu_program.tree)

    def add_optimizations(self, list_optim_cmds: List[TiramisuAction]) -> None:
        """
        Adds a list of optimizations to the schedule while maintaining the schedule tree. The order of the optimizations in the list is important.

        Parameters
        ----------
        `list_optim_cmds` : `List[TiramisuAction]`
            The list of optimizations to be added to the schedule.
        """
        if self.tree is None:
            raise Exception("No Tiramisu program to apply the schedule to")

        self.legality = None

        for optim_cmd in list_optim_cmds:
            if optim_cmd in self.optims_list:
                continue
            # check if the iterators of the optim are renamed
            optim_cmd.check_renamed_iterators(self.tree)
            # additional checks to see if optimiaztion can be applied
            optim_cmd.verify_conditions(self.tree)

            if optim_cmd.is_fusion():
                # Fusion is a special case, we need to transform the tree before setting the string representations to get the right order of computations
                optim_cmd.transform_tree(self.tree)
                optim_cmd.set_string_representations(self.tree)
            else:
                optim_cmd.set_string_representations(self.tree)
                optim_cmd.transform_tree(self.tree)

            self.optims_list.append(optim_cmd)

    def pop_optimization(self) -> TiramisuAction:
        """
        Removes the last optimization from the schedule and returns it.
        """
        return self.optims_list.pop()

    def apply_schedule(self, nb_exec_tiems=1) -> List[float]:
        """
        Applies the schedule to the Tiramisu program.

        Parameters
        ----------
        `nb_exec_times` : int
            The number of times the Tiramisu program will be executed after applying the schedule.
        Returns
        -------
        The execution time of the Tiramisu program after applying the schedule.
        """
        if self.tiramisu_program is None:
            raise Exception("No Tiramisu program to apply the schedule to")

        if self.legality is None and self.optims_list:
            self.is_legal()

        if self.legality == False:
            raise Exception("Schedule is not legal")

        return CompilingService.get_cpu_exec_times(
            self.tiramisu_program, self.optims_list, nb_exec_tiems
        )

    def is_legal(self) -> bool:
        """
        Checks if the schedule is legal.

        Returns
        -------
        Boolean indicating if the schedule is legal.
        """

        if self.tiramisu_program is None:
            raise Exception("No Tiramisu program to apply the schedule to")

        self.legality = CompilingService.compile_legality(self)
        return self.legality

    @classmethod
    def from_sched_str(
        cls, tiramisu_program: TiramisuProgram, sched_str: str
    ) -> "Schedule":
        schedule = cls(tiramisu_program)
        assert schedule.tree
        for optimization_str in sched_str.split("|"):
            if optimization_str == "":
                continue
            if optimization_str[0] == "P":
                # extract loop level and comps using P\(L(\d),comps=\[([\w',]*)
                regex = r"P\(L(\d),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    loop_level = int(match.group(1))
                    comps = match.group(2).split(",")
                    comps = [comp.strip("' ") for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Parallelization(
                                [schedule.tree.get_comp_iterator(comps[0], loop_level)],
                                schedule.tree,
                            )
                        ]
                    )

            elif optimization_str[0] == "U":
                # extract loop level, factor and comps using U\(L(\d),(\d+),comps=\[([\w',]*)\]\)
                regex = r"U\(L(\d),(\d+),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    loop_level = int(match.group(1))
                    factor = int(match.group(2))
                    comps = match.group(3).split(",")
                    comps = [comp.strip("' ") for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Unrolling(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], loop_level
                                    ),
                                    factor,
                                ],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[0] == "I":
                regex = r"I\(L(\d),L(\d),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    first_loop_level = int(match.group(1))
                    second_loop_level = int(match.group(2))
                    comps = match.group(3).split(",")
                    comps = [comp.strip("' ") for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Interchange(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], first_loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[0], second_loop_level
                                    ),
                                ],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[0] == "R":
                regex = r"R\(L(\d),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    loop_level = int(match.group(1))
                    comps = match.group(2).split(",")
                    comps = [comp.strip("' ") for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Reversal(
                                [schedule.tree.get_comp_iterator(comps[0], loop_level)],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[:2] == "T2":
                regex = r"T2\(L(\d),L(\d),(\d+),(\d+),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    outer_loop_level = int(match.group(1))
                    inner_loop_level = int(match.group(2))
                    outer_loop_factor = int(match.group(3))
                    inner_loop_factor = int(match.group(4))
                    comps = match.group(5).split(",")
                    comps = [comp.strip("' ").strip() for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Tiling2D(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], outer_loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[0], inner_loop_level
                                    ),
                                    outer_loop_factor,
                                    inner_loop_factor,
                                ],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[:2] == "T3":
                regex = (
                    r"T3\(L(\d),L(\d),L(\d),(\d+),(\d+),(\d+),comps=\[([\w', ]*)\]\)"
                )
                match = re.match(regex, optimization_str)
                if match:
                    outer_loop_level = int(match.group(1))
                    middle_loop_level = int(match.group(2))
                    inner_loop_level = int(match.group(3))
                    outer_loop_factor = int(match.group(4))
                    middle_loop_factor = int(match.group(5))
                    inner_loop_factor = int(match.group(6))
                    comps = match.group(7).split(",")
                    comps = [comp.strip("' ").strip() for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Tiling3D(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], outer_loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[0], middle_loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[0], inner_loop_level
                                    ),
                                    outer_loop_factor,
                                    middle_loop_factor,
                                    inner_loop_factor,
                                ],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[0] == "S":
                regex = r"S\(L(\d),L(\d),(\d+),(\d+),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    outer_loop_level = int(match.group(1))
                    inner_loop_level = int(match.group(2))
                    outer_loop_factor = int(match.group(3))
                    inner_loop_factor = int(match.group(4))
                    comps = match.group(5).split(",")
                    comps = [comp.strip("' ").strip() for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Skewing(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], outer_loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[0], inner_loop_level
                                    ),
                                    outer_loop_factor,
                                    inner_loop_factor,
                                ],
                                schedule.tree,
                            )
                        ]
                    )
            elif optimization_str[0] == "F":
                regex = r"F\(L(\d),comps=\[([\w', ]*)\]\)"
                match = re.match(regex, optimization_str)
                if match:
                    loop_level = int(match.group(1))
                    comps = match.group(2).split(",")
                    comps = [comp.strip("' ").strip() for comp in comps]
                    schedule.add_optimizations(
                        [
                            tiramisu_actions.Fusion(
                                [
                                    schedule.tree.get_comp_iterator(
                                        comps[0], loop_level
                                    ),
                                    schedule.tree.get_comp_iterator(
                                        comps[1], loop_level
                                    ),
                                ],
                                schedule.tree,
                            )
                        ]
                    )

        return schedule

    def __str__(self) -> str:
        """
        Generates a string representation of the schedule.
        """

        sched_str = "|".join([str(optim) for optim in self.optims_list])

        return sched_str

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> Schedule:
        """
        Returns a copy of the schedule.
        """
        new_schedule = Schedule(self.tiramisu_program)
        new_schedule.add_optimizations(self.optims_list)
        return new_schedule
