from __future__ import annotations

from typing import List, TYPE_CHECKING
from athena.tiramisu.compiling_service import CompilingService
from athena.tiramisu.optimization_command import OptimizationType

if TYPE_CHECKING:
    from .optimization_command import OptimizationCommand
from athena.tiramisu.tiramisu_program import TiramisuProgram


class Schedule:
    def __init__(self, tiramisu_program: TiramisuProgram) -> None:
        self.tiramisu_program = tiramisu_program
        self.optims_list: List[OptimizationCommand] = []

    def add_optimization(self, optim_cmd: OptimizationCommand) -> None:
        self.optims_list.append(optim_cmd)

    def apply_schedule(self, tiramisu_program: TiramisuProgram = None) -> None:
        if tiramisu_program is None:
            tiramisu_prog = self.tiramisu_program
        else:
            tiramisu_prog = tiramisu_program
        return CompilingService.get_cpu_exec_times(tiramisu_prog, self.optims_list, 1)

    def is_legal(self) -> bool:
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
            optim for optim in self.optims_list if optim.type == OptimizationType.FUSION
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

                if transformation.type == OptimizationType.INTERCHANGE:
                    sched_str += (
                        "I(L"
                        + str(transformation.params_list[0])
                        + ",L"
                        + str(transformation.params_list[1])
                        + ")"
                    )

                elif transformation.type == OptimizationType.REVERSAL:
                    sched_str += f"R(L{str(transformation.params_list[0])})"

                elif transformation.type == OptimizationType.SKEWING:
                    sched_str += (
                        "S(L"
                        + str(transformation.params_list[0])
                        + ",L"
                        + str(transformation.params_list[1])
                        + ","
                        + str(transformation.params_list[2])
                        + ","
                        + str(transformation.params_list[3])
                        + ")"
                    )

                elif transformation.type == OptimizationType.PARALLELIZATION:
                    sched_str += "P(L" + str(transformation.params_list[0]) + ")"

                elif transformation.type == OptimizationType.TILING:
                    # T2
                    if len(transformation.params_list) == 4:
                        first_dim_index = transformation.params_list[0]
                        second_dim_index = transformation.params_list[1]
                        first_factor = transformation.params_list[2]
                        second_factor = transformation.params_list[3]
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
                        first_dim_index = transformation.params_list[0]
                        second_dim_index = transformation.params_list[1]
                        third_dim_index = transformation.params_list[2]
                        first_factor = transformation.params_list[3]
                        second_factor = transformation.params_list[4]
                        third_factor = transformation.params_list[5]
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

                elif transformation.type == OptimizationType.UNROLLING:
                    dim_index = transformation.params_list[name][0]
                    unrolling_factor = transformation.params_list[name][1]
                    sched_str += (
                        "U(L" + str(dim_index) + "," + str(unrolling_factor) + ")"
                    )

        return sched_str

    def __repr__(self) -> str:
        return self.__str__()
