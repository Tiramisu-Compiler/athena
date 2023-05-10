import time
from athena.data.dataset_actor.dataset_actor import DatasetActor
from athena.tiramisu.optimization_command import OptimizationCommand, OptimizationType
from athena.tiramisu.schedule import Schedule
from athena.tiramisu.tiramisu_program import TiramisuProgram
import tiramisu
from athena.utils.config import BaseConfig


if __name__ == "__main__":
    BaseConfig.init()
    # dataset_actor = DatasetActor(BaseConfig.base_config.dataset, "cpu")
    # tiramisu_func = dataset_actor.get_function_by_name("function_matmul_MEDIUM")

    tiramisu_func = TiramisuProgram.from_file(
        "_tmp/function_matmul_MEDIUM.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.cpp",
        "_tmp/function_matmul_MEDIUM_wrapper.h",
    )

    print(tiramisu_func)

    print(f"Unoptimized: {Schedule(tiramisu_func).apply_schedule()}")
    # Create a schedule
    schedule = Schedule(tiramisu_func)

    # Add optimizations to the schedule
    schedule.add_optimization(
        OptimizationCommand(OptimizationType.PARALLELIZATION, [0], ["comp02"])
    )
    start_time = time.time()
    legality = schedule.is_legal()
    end_time = time.time()
    print(f"Legality check time: {end_time - start_time}")
    if legality:
        print(f"Schedule: {schedule} is legal")
        print(f"Optimized: {schedule.apply_schedule()}")
