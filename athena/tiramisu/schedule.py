from __future__ import annotations
from copy import deepcopy

from typing import List, TYPE_CHECKING
from athena.tiramisu.compiling_service import CompilingService
from athena.tiramisu.tiramisu_actions.tiramisu_action import TiramisuActionType

if TYPE_CHECKING:
    from .tiramisu_actions.tiramisu_action import TiramisuAction
from athena.tiramisu.tiramisu_program import TiramisuProgram


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
