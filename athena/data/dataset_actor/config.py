
from dataclasses import dataclass
from typing import Dict


class DatasetFormat:
    # Both the CPP code and the data of the functions are loaded from PICKLE files
    PICKLE = "PICKLE"
    # We look for informations in the pickle files, if something is missing we get it from cpp files in a dynamic way
    HYBRID = "HYBRID"

    @staticmethod
    def from_string(s):
        if s == "PICKLE":
            return DatasetFormat.PICKLE
        elif s == "HYBRID":
            return DatasetFormat.HYBRID
        else:
            raise ValueError("Unknown dataset format")


@dataclass
class DatasetConfig:
    dataset_format: DatasetFormat = DatasetFormat.HYBRID
    cpps_path: str = ""
    dataset_path: str = ""
    save_path: str = ""
    shuffle: bool = False
    seed: int = None
    saving_frequency: int = 10000
    wrappers_path: str = ""

    def __init__(self, dataset_config_dict: Dict):
        self.dataset_format = DatasetFormat.from_string(
            dataset_config_dict["dataset_format"]
        )
        self.cpps_path = dataset_config_dict["cpps_path"]
        self.dataset_path = dataset_config_dict["dataset_path"]
        self.save_path = dataset_config_dict["save_path"]
        self.shuffle = dataset_config_dict["shuffle"]
        self.seed = dataset_config_dict["seed"]
        self.saving_frequency = dataset_config_dict["saving_frequency"]
        self.wrappers_path = dataset_config_dict["wrappers_path"]

        if dataset_config_dict["is_benchmark"]:
            self.dataset_path = (
                dataset_config_dict["benchmark_dataset_path"]
                if dataset_config_dict["benchmark_dataset_path"]
                else self.dataset_path
            )
            self.cpps_path = (
                dataset_config_dict["benchmark_cpp_files"]
                if dataset_config_dict["benchmark_cpp_files"]
                else self.cpps_path
            )
            self.wrappers_path = (
                dataset_config_dict["benchmark_wrappers_path"]
                if dataset_config_dict["benchmark_wrappers_path"]
                else self.wrappers_path
            )
