from functools import reduce
import xml.etree.ElementTree as ET

import maplib.parameters as params

from maplib.svg.svg_element import Defs
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Svg
from maplib.svg.path_types import CommandPath
from maplib.tools.simple_functions import merge_dicts
from maplib.tools.simple_functions import sort_dict_by_key
from maplib.tools.tex_json_file_tools import update_generated_tex_in_json


class Canvas(object):
    def __init__(self, file_name):
        self.init_background()
        self.init_tex_objs_list()
        self.construct()
        self.define_path()
        self.modify_json()
        self.write_to_file(file_name)

    def construct(self):
        """
        Implemented in subclasses.
        """
        pass

    def init_background(self):
        self.root = Svg()
        self.defs = Defs()
        self.root.append(self.defs)
        self.canvas = Group("canvas").flip_y()
        self.root.append(self.canvas)
        self.path_group = Group("paths")
        self.define(self.path_group)

    def init_tex_objs_list(self):
        self.global_tex_objs = []

    def define(self, component):
        if hasattr(component, "tex_objs"):
            self.global_tex_objs.extend(component.tex_objs)
        if hasattr(component, "template"):
            self.define(component.template)
        self.defs.append(component)

    def draw(self, id_name):
        self.canvas.use(id_name)

    def define_path(self):
        global_tex_paths_cmd_dict = sort_dict_by_key(reduce(
            merge_dicts,
            [tex_obj.tex_paths_cmd_dict for tex_obj in self.global_tex_objs]
        ))
        for path_id, path_cmd in global_tex_paths_cmd_dict.items():
            path_obj = CommandPath(path_id, path_cmd)
            self.path_group.append(path_obj)

    def modify_json(self):
        update_generated_tex_in_json(self.global_tex_objs)
    
    def modify_svg_str(self, string):
        string = params.SVG_HEAD + string
        string = string.replace(" />", "/>")
        string = string.replace("><", ">\n<")
        return string
    
    def modify_svg_file(self, file_name):
        with open(file_name, "r") as input_file:
            string = "".join(input_file.readlines())
        result = self.modify_svg_str(string)
        with open(file_name, "w") as output_file:
            output_file.write(result)

    def write_to_file(self, file_name):
        file_body = ET.ElementTree(self.root)
        file_body.write(file_name)
        self.modify_svg_file(file_name)

