from functools import reduce
import xml.etree.ElementTree as ElementTree

from maplib.svg.svg_element import Defs
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Svg
from maplib.svg.path_types import CommandPath
from maplib.tools.json_file_tools import update_generated_tex_in_json
from maplib.tools.simple_functions import merge_dicts
from maplib.tools.simple_functions import sort_dict_by_key


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
        root = Svg()
        defs = Defs()
        root.append(defs)
        canvas = Group("canvas").flip_y()
        root.append(canvas)
        path_group = Group("paths")
        self.root = root
        self.defs = defs
        self.canvas = canvas
        self.path_group = path_group
        self.define(path_group)

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

    @staticmethod
    def modify_svg_str(string):
        string = string.replace(" />", "/>")
        string = string.replace("><", ">\n<")
        return string

    @staticmethod
    def modify_svg_file(file_name):
        with open(file_name, "r") as input_file:
            string = "".join(input_file.readlines())
        result = Canvas.modify_svg_str(string)
        with open(file_name, "w") as output_file:
            output_file.write(result)

    def write_to_file(self, file_name):
        file_body = ElementTree.ElementTree(self.root)
        file_body.write(file_name)
        Canvas.modify_svg_file(file_name)
