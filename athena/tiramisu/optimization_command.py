from enum import Enum


class OptimizationType(Enum):
    """The type of an optimization command."""

    INTERCHANGE = 0
    TILING = 1
    PARALLELIZATION = 2
    SKEWING = 3
    UNROLLING = 4
    FUSION = 5
    REVERSAL = 6


class OptimizationCommand:
    def __init__(self, type: OptimizationType, params: list, comps: list):
        self.params_list = params
        # A list of concerned computations of the actions
        self.comps = comps
        self.type = type
        self.tiramisu_optim_str = self.get_tiramisu_optim_str()

    def get_tiramisu_optim_str(self):
        """Convert the optimization command into Tiramisu code.
        Returns:
            str: The tiramisu snippet that represents the optimization command.
        """

        if self.type == OptimizationType.INTERCHANGE:
            interchange_str = (
                ".interchange(" + ",".join([str(p) for p in self.params_list]) + ");"
            )
            optim_str = ""
            for comp in self.comps:
                optim_str += "\n\t{}".format(comp) + interchange_str
            return optim_str
        elif self.type == OptimizationType.SKEWING:
            assert len(self.params_list) == 4
            skewing_str = ".skew(" + ",".join([str(p) for p in self.params_list]) + ");"
            optim_str = ""
            for comp in self.comps:
                optim_str += "\n\t{}".format(comp) + skewing_str
            return optim_str

        elif self.type == OptimizationType.PARALLELIZATION:
            assert len(self.params_list) == 1
            return (
                "\n\t"
                + self.comps[0]
                + ".tag_parallel_level("
                + str(self.params_list[0])
                + ");"
            )

        elif self.type == OptimizationType.TILING:
            assert len(self.params_list) == 4 or len(self.params_list) == 6
            tiling_str = ".tile(" + ",".join([str(p) for p in self.params_list]) + ");"
            optim_str = ""
            for comp in self.comps:
                optim_str += "\n\t{}".format(comp) + tiling_str
            return optim_str
        elif self.type == OptimizationType.UNROLLING:
            optim_str = ""
            for comp in self.comps:
                unrolling_str = (
                    ".unroll("
                    + ",".join([str(p) for p in self.params_list[comp]])
                    + ");"
                )
                optim_str += "\n\t{}".format(comp) + unrolling_str
            return optim_str
        elif self.type == OptimizationType.REVERSAL:
            reversal_str = ".loop_reversal(" + str(self.params_list[0]) + ");"
            optim_str = ""
            for comp in self.comps:
                optim_str += "\n\t{}".format(comp) + reversal_str
            return optim_str
        elif self.type == OptimizationType.FUSION:
            # TODO : Recheck the right command for this
            optim_str = ""
            # prev_comp = self.comps[0]
            # for comp in self.comps[1:]:
            #     optim_str += ("\n\t {}".format(prev_comp) + ".then(" +
            #                   str(comp) + "," + str(self.params_list[0]) +
            #                   ");")
            #     prev_comp = comp
            optim_str = "\n\t" + self.comps[0]
            for comp in self.comps[1:]:
                optim_str += ".then(" + comp + "," + str(self.params_list[0]) + ")"
            optim_str += ";"
            return optim_str

    def __str__(self) -> str:
        return f"OptimizationCommand(type={self.type}, params={self.params_list}, comps={self.comps})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_interchange(self) -> bool:
        return self.type == OptimizationType.INTERCHANGE

    def is_tiling(self) -> bool:
        return self.type == OptimizationType.TILING

    def is_parallelization(self) -> bool:
        return self.type == OptimizationType.PARALLELIZATION

    def is_skewing(self) -> bool:
        return self.type == OptimizationType.SKEWING

    def is_unrolling(self) -> bool:
        return self.type == OptimizationType.UNROLLING

    def is_fusion(self) -> bool:
        return self.type == OptimizationType.FUSION

    def is_reversal(self) -> bool:
        return self.type == OptimizationType.REVERSAL
