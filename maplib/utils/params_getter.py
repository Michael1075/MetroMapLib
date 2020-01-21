import argparse
import importlib
import json
import os

import maplib.constants as consts

from maplib.tools.file_tools import get_file_basename
from maplib.tools.file_tools import get_relative_path
from maplib.tools.numpy_type_tools import np_float


class Getter(object):
    def __init__(self):
        self.PROJECT_CITY_NAME = Getter.get_project_city_name()
        self.load_dirs()
        self.load_database()
        self.load_params()
        self.load_size()

    @staticmethod
    def check_valid_folder_path(folder_path):
        return os.path.isdir(folder_path) and all([
            required_files in os.listdir(folder_path)
            for required_files in (
                "input.json",
                "parameters.py",
                "tex.json",
                "metro_logo.svg",
            )
        ])
    
    @staticmethod
    def get_project_city_name():
        file_dir = consts.FILE_DIR
        possible_folder_names = []
        for folder_name in os.listdir(file_dir):
            if folder_name != "template_file":
                folder_path = os.path.join(file_dir, folder_name)
                if Getter.check_valid_folder_path(folder_path):
                    possible_folder_names.append(folder_name)
        possible_folder_names.sort()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-p",
            "--project",
            dest="project_name",
            choices=possible_folder_names,
            default=consts.DEFAULT_PROJECT_CITY_NAME,
            help=consts.CMD_PARAMETER_HELP_MSG,
        )
        args = parser.parse_args()
        return args.project_name

    def load_dirs(self):
        project_dir = os.path.join(consts.FILE_DIR, self.PROJECT_CITY_NAME)
        self.PROJECT_DIR = project_dir
        self.INPUT_JSON_DIR = os.path.join(project_dir, "input.json")
        self.PARAMETERS_DIR = os.path.join(project_dir, "parameters.py")
        self.TEX_JSON_DIR = os.path.join(project_dir, "tex.json")
        self.METRO_LOGO_DIR = os.path.join(project_dir, "metro_logo.svg")
        self.OUTPUT_SVG_DIR = os.path.join(project_dir, "output.svg")

    def load_database(self):
        with open(self.INPUT_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
            self.INPUT_DATABASE_DICT = json.load(input_file)
        with open(self.TEX_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
            self.GLOBAL_TEX_DICT = json.load(input_file)

    def load_params(self):
        params_path = get_relative_path(self.PARAMETERS_DIR)
        pkg_name = get_file_basename(params_path).replace("\\", ".")
        params_module = importlib.import_module(pkg_name)
        for key, val in params_module.__dict__.items():
            if "__" not in key and key not in ("consts", "np_float", "Color"):
                self.__setattr__(key, val)

    def load_size(self):
        self.FULL_SIZE = np_float(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.BODY_SIZE = np_float(self.BODY_WIDTH, self.BODY_HEIGHT)


getter = Getter()


class Container(object):
    def __init__(self):
        self._params = getter

    @property
    def params(self):
        return self._params
