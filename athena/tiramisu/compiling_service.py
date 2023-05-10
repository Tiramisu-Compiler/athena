from __future__ import annotations

import logging
import os
import subprocess
import re
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from athena.tiramisu.optimization_command import OptimizationCommand
    from athena.tiramisu.schedule import Schedule
    from athena.tiramisu.tiramisu_program import TiramisuProgram

from athena.utils.config import BaseConfig


class CompilingService:
    @classmethod
    def compile_legality(
        cls, tiramisu_program: TiramisuProgram, optims_list: List[OptimizationCommand]
    ):
        output_path = os.path.join(
            BaseConfig.base_config.workspace, f"{tiramisu_program.name}_legality"
        )

        cpp_code = cls.get_legality_code(
            tiramisu_program=tiramisu_program, optims_list=optims_list
        )
        return cls.run_cpp_code(cpp_code=cpp_code, output_path=output_path)

    @classmethod
    def get_legality_code(
        cls, tiramisu_program: TiramisuProgram, optims_list: List[OptimizationCommand]
    ):
        comps = tiramisu_program.comps
        first_comp = tiramisu_program.comps[0]
        # Add code to the original file to get legality result
        legality_check_lines = """\n\tprepare_schedules_for_legality_checks();\n\tperform_full_dependency_analysis();\n\tbool is_legal=true;"""
        for optim in optims_list:
            if optim.is_parallelization():
                legality_check_lines += f"\n\tis_legal &= loop_parallelization_is_legal({optim.params_list[0]}, {{&{first_comp}}});\n"
            # elif optim.is_unrolling():
            #     for branch in schedule_object.branches:
            #         comps = branch["comps"]
            #         level = len(branch["iterators"]) - 1
            #         legality_check_lines += print(
            #             f"\n\tis_legal &= loop_unrolling_is_legal({level}, {{{', '.join([f'&{comp}' for comp in comps])}}});")
            legality_check_lines += optim.tiramisu_optim_str + "\n"

        legality_check_lines += """
            is_legal &= check_legality_of_function();   
            std::cout << is_legal;
            """
        # Paste the lines responsable of checking legality of schedule in the cpp file
        cpp_code = tiramisu_program.original_str.replace(
            tiramisu_program.code_gen_line, legality_check_lines
        )
        return cpp_code

    @classmethod
    def compile_annotations(cls, tiramisu_program):
        # TODO : add getting tree structure object from executing the file instead of building it
        output_path = os.path.join(
            BaseConfig.base_config.workspace, f"{tiramisu_program.name}_annotations"
        )
        # Add code to the original file to get json annotations

        get_json_lines = """
            auto ast = tiramisu::auto_scheduler::syntax_tree(tiramisu::global::get_implicit_function(), {});
            std::string program_json = tiramisu::auto_scheduler::evaluate_by_learning_model::get_program_json(ast);
            std::cout << program_json;
            """

        # Paste the lines responsable of generating the program json tree in the cpp file
        cpp_code = tiramisu_program.original_str.replace(
            tiramisu_program.code_gen_line, get_json_lines
        )
        return cls.run_cpp_code(cpp_code=cpp_code, output_path=output_path)

    @classmethod
    def run_cpp_code(cls, cpp_code: str, output_path: str):
        env_vars = [
            f"export {key}={value}"
            for key, value in BaseConfig.base_config.env_vars.items()
        ]
        if BaseConfig.base_config.tiramisu.is_new_tiramisu:
            # Making the tiramisu root path explicit to the env
            shell_script = [
                # Compile intermidiate tiramisu file
                "$CXX -I$TIRAMISU_ROOT/3rdParty/Halide/install/include -I$TIRAMISU_ROOT/include -I$TIRAMISU_ROOT/3rdParty/isl/include  -Wl,--no-as-needed -ldl -g -fno-rtti   -lpthread -std=c++17 -O0 -o {}.o -c -x c++ -".format(
                    output_path
                ),
                # Link generated file with executer
                "$CXX -Wl,--no-as-needed -ldl -g -fno-rtti -lpthread -std=c++17 -O0 {}.o -o {}.out   -L$TIRAMISU_ROOT/build  -L$TIRAMISU_ROOT/3rdParty/Halide/install/lib64  -L$TIRAMISU_ROOT/3rdParty/isl/build/lib  -Wl,-rpath,$TIRAMISU_ROOT/build:$TIRAMISU_ROOT/3rdParty/Halide/install/lib64:$TIRAMISU_ROOT/3rdParty/isl/build/lib -ltiramisu -ltiramisu_auto_scheduler -lHalide -lisl".format(
                    output_path, output_path
                ),
                # Run the program
                "{}.out".format(output_path),
                # Clean generated files
                "rm {}*".format(output_path),
            ]
        else:
            shell_script = [
                # Compile intermidiate tiramisu file
                "$CXX -I$TIRAMISU_ROOT/3rdParty/Halide/include -I$TIRAMISU_ROOT/include -I$TIRAMISU_ROOT/3rdParty/isl/include  -Wl,--no-as-needed -ldl -g -fno-rtti   -lpthread -std=c++11 -O0 -o {}.o -c -x c++ -".format(
                    output_path
                ),
                # Link generated file with executer
                "$CXX -Wl,--no-as-needed -ldl -g -fno-rtti -lpthread -std=c++11 -O0 {}.o -o {}.out   -L$TIRAMISU_ROOT/build  -L$TIRAMISU_ROOT/3rdParty/Halide/lib  -L$TIRAMISU_ROOT/3rdParty/isl/build/lib  -Wl,-rpath,$TIRAMISU_ROOT/build:$TIRAMISU_ROOT/3rdParty/Halide/lib:$TIRAMISU_ROOT/3rdParty/isl/build/lib -ltiramisu -ltiramisu_auto_scheduler -lHalide -lisl".format(
                    output_path, output_path
                ),
                # Run the program
                "{}.out".format(output_path),
                # Clean generated files
                "rm {}*".format(output_path),
            ]
        try:
            compiler = subprocess.run(
                ["\n".join(env_vars + shell_script)],
                input=cpp_code,
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
            return compiler.stdout if compiler.stdout != "" else "0"
        except subprocess.CalledProcessError as e:
            print("Process terminated with error code", e.returncode)
            print("Error output:", e.stderr)
            return "0"
        except Exception as e:
            print(e)
            return "0"

    @classmethod
    def call_skewing_solver(cls, schedule_object, optim_list, params):
        legality_cpp_code = cls.get_legality_code(schedule_object, optim_list)
        to_replace = re.findall(r"std::cout << is_legal;", legality_cpp_code)[0]
        header = """
        function * fct = tiramisu::global::get_implicit_function();\n"""
        legality_cpp_code = legality_cpp_code.replace(
            "is_legal &= check_legality_of_function();", ""
        )
        legality_cpp_code = legality_cpp_code.replace("bool is_legal=true;", "")
        legality_cpp_code = re.sub(
            r"is_legal &= loop_parallelization_is_legal.*\n", "", legality_cpp_code
        )
        legality_cpp_code = re.sub(
            r"is_legal &= loop_unrolling_is_legal.*\n", "", legality_cpp_code
        )

        solver_lines = (
            header
            + "\n\tauto auto_skewing_result = fct->skewing_local_solver({"
            + ", ".join([f"&{comp}" for comp in schedule_object.comps])
            + "}"
            + ",{},{},1);\n".format(*params)
        )

        solver_lines += """    
        std::vector<std::pair<int,int>> outer1, outer2,outer3;
        tie( outer1,  outer2,  outer3 )= auto_skewing_result;
        if (outer1.size()>0){
            std::cout << outer1.front().first;
            std::cout << ",";
            std::cout << outer1.front().second;
            std::cout << ",";
        }else {
            std::cout << "None,None,";
        }
        if(outer2.size()>0){
            std::cout << outer2.front().first;
            std::cout << ",";
            std::cout << outer2.front().second;
            std::cout << ",";
        }else {
            std::cout << "None,None,";
        }
        if(outer3.size()>0){
            std::cout << outer3.front().first;
            std::cout << ",";
            std::cout << outer3.front().second;
            std::cout << ",";
        }else {
            std::cout << "None,None,";
        }
        
            """

        solver_code = legality_cpp_code.replace(to_replace, solver_lines)
        output_path = os.path.join(
            BaseConfig.base_config.workspace, f"{schedule_object.prog.name}skew_solver"
        )
        result_str = cls.run_cpp_code(cpp_code=solver_code, output_path=output_path)
        if not result_str:
            return None
            # Refer to function run_cpp_code to see from where the "0" comes from
        elif result_str == "0":
            return None
        result_str = result_str.split(",")
        # Skewing Solver returns 3 solutions in form of tuples, the first tuple is for outer parallelism ,
        # second is for inner parallelism , and last one is for locality, we are going to use the first preferably
        # if availble , else , we are going to use the scond one if available, this policy of choosing factors may change
        # in later versions!
        # The compiler in our case returns a tuple of type : (fac0,fac1,fac2,fac3,fac4,fac5) each 2 factors represent the
        # solutions mentioned above
        if result_str[0] != "None":
            # Means we have a solution for outer parallelism
            fac1 = int(result_str[0])
            fac2 = int(result_str[1])
            return fac1, fac2
        if result_str[2] != "None":
            # Means we have a solution for inner parallelism
            fac1 = int(result_str[2])
            fac2 = int(result_str[3])
            return fac1, fac2
        else:
            return None

    @classmethod
    def get_schedule_code(
        cls, tiramisu_program, optims_list: List[OptimizationCommand]
    ):
        # Add code to the original file to get the schedule code
        schedule_code = ""
        for optim in optims_list:
            schedule_code += optim.tiramisu_optim_str + "\n"

        # Add code gen line to the schedule code
        schedule_code += "\n\t" + tiramisu_program.code_gen_line + "\n"
        # Paste the lines responsable of checking legality of schedule in the cpp file
        cpp_code = tiramisu_program.original_str.replace(
            tiramisu_program.code_gen_line, schedule_code
        )
        cpp_code = cpp_code.replace(
            f"// {tiramisu_program.wrapper_str}", tiramisu_program.wrapper_str
        )
        return cpp_code

    @classmethod
    def write_to_disk(cls, cpp_code: str, output_path: str, extension: str = ".cpp"):
        with open(output_path + extension, "w") as f:
            f.write(cpp_code)

    @classmethod
    def get_cpu_exec_times(
        cls,
        tiramisu_program,
        optims_list: List[OptimizationCommand],
        max_runs: int = None,
    ) -> List[float]:
        if max_runs is None:
            max_runs = BaseConfig.base_config.tiramisu.max_runs
        # Get the code of the schedule
        cpp_code = cls.get_schedule_code(tiramisu_program, optims_list)
        # Write the code to a file
        output_path = os.path.join(
            BaseConfig.base_config.workspace, tiramisu_program.name
        )

        cls.write_to_disk(cpp_code, output_path + "_schedule")

        # write the wrappers
        cls.write_to_disk(tiramisu_program.wrappers["cpp"], output_path + "_wrapper")
        cls.write_to_disk(
            tiramisu_program.wrappers["h"], output_path + "_wrapper", ".h"
        )

        env_vars = [
            f"export {key}={value}"
            for key, value in BaseConfig.base_config.env_vars.items()
        ]

        if BaseConfig.base_config.tiramisu.is_new_tiramisu:
            # Making the tiramisu root path explicit to the env
            shell_script = [
                f"cd {BaseConfig.base_config.workspace}",
                # Compile intermidiate tiramisu file
                f"$CXX -I$TIRAMISU_ROOT/3rdParty/Halide/install/include -I$TIRAMISU_ROOT/include -I$TIRAMISU_ROOT/3rdParty/isl/include  -Wl,--no-as-needed -ldl -g -fno-rtti   -lpthread -std=c++17 -O0 -o {tiramisu_program.name}.o -c {tiramisu_program.name}_schedule.cpp",
                # Link generated file with executer
                f"$CXX -Wl,--no-as-needed -ldl -g -fno-rtti -lpthread -std=c++17 -O0 {tiramisu_program.name}.o -o {tiramisu_program.name}.out   -L$TIRAMISU_ROOT/build  -L$TIRAMISU_ROOT/3rdParty/Halide/install/lib64  -L$TIRAMISU_ROOT/3rdParty/isl/build/lib  -Wl,-rpath,$TIRAMISU_ROOT/build:$TIRAMISU_ROOT/3rdParty/Halide/install/lib64:$TIRAMISU_ROOT/3rdParty/isl/build/lib -ltiramisu -ltiramisu_auto_scheduler -lHalide -lisl",
                # Run the generator
                f"./{tiramisu_program.name}.out",
                # compile the wrapper
                f"$CXX -shared -o {tiramisu_program.name}.o.so {tiramisu_program.name}.o",
                f"$CXX -std=c++17 -fno-rtti -I$TIRAMISU_ROOT/include -I$TIRAMISU_ROOT/3rdParty/Halide/install/include -I$TIRAMISU_ROOT/3rdParty/isl/include/ -I$TIRAMISU_ROOT/benchmarks -L$TIRAMISU_ROOT/build -L$TIRAMISU_ROOT/3rdParty/Halide/install/lib64/ -L$TIRAMISU_ROOT/3rdParty/isl/build/lib -o {tiramisu_program.name}_wrapper -ltiramisu -lHalide -ldl -lpthread -lm -Wl,-rpath,$TIRAMISU_ROOT/build {tiramisu_program.name}_wrapper.cpp ./{tiramisu_program.name}.o.so -ltiramisu -lHalide -ldl -lpthread -lm -lisl",
            ]

        else:
            # TODO
            raise NotImplementedError

        run_script = [
            # cd to the workspace
            f"cd {BaseConfig.base_config.workspace}",
            #  set the env variables
            f"export DYNAMIC_RUNS=0",
            f"export MAX_RUNS={max_runs}",
            f"export NB_EXEC={max_runs}",
            # run the wrapper
            f"./{tiramisu_program.name}_wrapper",
            # Clean generated files
            # f"rm {tiramisu_program.name}*",
        ]
        try:
            # run the compilation of the generator and wrapper
            compiler = subprocess.run(
                [" ; ".join(env_vars + shell_script)],
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
            # run the wrapper and get the execution times
            compiler = subprocess.run(
                [" ; ".join(env_vars + run_script)],
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )

            # Extract the execution times from the output and return the minimum
            if compiler.stdout:
                results = [float(x) for x in compiler.stdout.split()]
                return results
            else:
                logging.error("No output from schedule execution")
                logging.error(compiler.stderr)
                logging.error(compiler.stdout)
                logging.error(
                    f"The following schedule execution crashed: {tiramisu_program.name}, schedule: {optims_list} \n\n {cpp_code}\n\n"
                )
                raise ScheduleExecutionCrashed("No output from schedule execution")
        except subprocess.CalledProcessError as e:
            print("Process terminated with error code", e.returncode)
            print("Error output:", e.stderr)
            print("Output:", e.stdout)
            raise ScheduleExecutionCrashed(
                f"Schedule execution crashed: function: {tiramisu_program.name}, schedule: {optims_list}"
            )
        except Exception as e:
            print(e)
            raise e


class ScheduleExecutionCrashed(Exception):
    "Raised when the execution of the schedule crashes"
    pass
