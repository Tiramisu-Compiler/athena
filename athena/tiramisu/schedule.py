from __future__ import annotations

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

    def __init__(self, tiramisu_program: TiramisuProgram) -> None:
        self.tiramisu_program = tiramisu_program
        self.optims_list: List[TiramisuAction] = []

    def add_optimization(self, optim_cmd: TiramisuAction) -> None:
        self.optims_list.append(optim_cmd)

    def pop_optimization(self) -> TiramisuAction:
        return self.optims_list.pop()

    def apply_schedule(
        self, tiramisu_program: TiramisuProgram = None, nb_exec_tiems=1
    ) -> List[float]:
        """
        Applies the schedule to the Tiramisu program.

        Parameters
        ----------
        `tiramisu_program` : TiramisuProgram
            The Tiramisu program to which the schedule will be applied. If None, the schedule will be applied to the Tiramisu program passed to the constructor.
        `nb_exec_times` : int
            The number of times the Tiramisu program will be executed after applying the schedule.
        Returns
        -------
        The execution time of the Tiramisu program after applying the schedule.
        """
        if tiramisu_program is None:
            tiramisu_prog = self.tiramisu_program
        else:
            tiramisu_prog = tiramisu_program
        return CompilingService.get_cpu_exec_times(
            tiramisu_prog, self.optims_list, nb_exec_tiems
        )

    def is_legal(self) -> bool:
        """
        Checks if the schedule is legal.

        Returns
        -------
        Boolean indicating if the schedule is legal.
        """
        return CompilingService.compile_legality(
            self.tiramisu_program, self.optims_list
        )

    def __str__(self) -> str:
        comp_names = list(
            set([comp for optim in self.optims_list for comp in optim.comps])
        )

        comp_names.sort()

        sched_str = ""

        # Add fusions first
        fusions = [
            optim
            for optim in self.optims_list
            if optim.type == TiramisuActionType.FUSION
        ]
        for fusion in fusions:
            sched_str += "F("
            for name in fusion.comps:
                sched_str += name + ","

            sched_str = sched_str[:-1]
            sched_str += ")"

        # Iterate over the comps and add their transformations
        for name in comp_names:
            sched_str += "{" + name + "}:"

            for transformation in self.optims_list:
                # Skip the transformation if it doesn't include the comp
                if name not in transformation.comps:
                    continue

                if transformation.type == TiramisuActionType.INTERCHANGE:
                    sched_str += (
                        "I(L"
                        + str(transformation.params[0])
                        + ",L"
                        + str(transformation.params[1])
                        + ")"
                    )

                elif transformation.type == TiramisuActionType.REVERSAL:
                    sched_str += f"R(L{str(transformation.params[0])})"

                elif transformation.type == TiramisuActionType.SKEWING:
                    sched_str += (
                        "S(L"
                        + str(transformation.params[0])
                        + ",L"
                        + str(transformation.params[1])
                        + ","
                        + str(transformation.params[2])
                        + ","
                        + str(transformation.params[3])
                        + ")"
                    )

                elif transformation.type == TiramisuActionType.PARALLELIZATION:
                    sched_str += "P(L" + str(transformation.params[0]) + ")"

                elif transformation.type == TiramisuActionType.TILING:
                    # T2
                    if len(transformation.params) == 4:
                        first_dim_index = transformation.params[0]
                        second_dim_index = transformation.params[1]
                        first_factor = transformation.params[2]
                        second_factor = transformation.params[3]
                        sched_str += (
                            "T2(L"
                            + str(first_dim_index)
                            + ",L"
                            + str(second_dim_index)
                            + ","
                            + str(first_factor)
                            + ","
                            + str(second_factor)
                            + ")"
                        )
                    # T3
                    else:
                        first_dim_index = transformation.params[0]
                        second_dim_index = transformation.params[1]
                        third_dim_index = transformation.params[2]
                        first_factor = transformation.params[3]
                        second_factor = transformation.params[4]
                        third_factor = transformation.params[5]
                        sched_str += (
                            "T3(L"
                            + str(first_dim_index)
                            + ",L"
                            + str(second_dim_index)
                            + ",L"
                            + str(third_dim_index)
                            + ","
                            + str(first_factor)
                            + ","
                            + str(second_factor)
                            + ","
                            + str(third_factor)
                            + ")"
                        )

                elif transformation.type == TiramisuActionType.UNROLLING:
                    dim_index = transformation.params[name][0]
                    unrolling_factor = transformation.params[name][1]
                    sched_str += (
                        "U(L" + str(dim_index) + "," + str(unrolling_factor) + ")"
                    )

        return sched_str

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> Schedule:
        """
        Returns a copy of the schedule.
        """
        new_schedule = Schedule(self.tiramisu_program)
        new_schedule.optims_list = self.optims_list.copy()
        return new_schedule
