import xml.etree.ElementTree as ET

from maplib.parameters import *

from maplib.svg.svg_element import Defs
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Svg
from maplib.svg.path_types import CommandPath
from maplib.svg.tex_instance import TexNameTemplate
from maplib.tools.file_tools import add_tex_to_json
from maplib.tools.file_tools import modify_svg_file


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
        Implemented in subclasses
        """
        pass

    def init_background(self):
        self.root = Svg(None)
        self.defs = Defs(None)
        self.root.append(self.defs)
        self.canvas = Group("canvas").flip_y()
        self.root.append(self.canvas)

    def init_tex_objs_list(self):
        self.global_tex_objs = []

    def define(self, component):
        self.defs.append(component)

    def define_tex(self, component):
        self.global_tex_objs.extend(component.tex_objs)
        self.define(component)

    def draw(self, id_name):
        self.canvas.use(id_name)

    def config(self, ClassName, id_name, *args):
        obj = ClassName(id_name, *args)
        if isinstance(obj, TexNameTemplate):
            self.define_tex(obj)
        else:
            self.define(obj)
            if hasattr(obj, "template_group"):
                self.define(obj.template_group)
        self.draw(id_name)

    def define_path(self):
        global_tex_path_id_set = set()
        for tex_obj in self.global_tex_objs:
            for path_id, path_cmd in tex_obj.tex_paths_cmd_dict.items():
                if path_id not in global_tex_path_id_set:
                    global_tex_path_id_set.add(path_id)
                    path_obj = CommandPath(path_id, path_cmd)
                    path_obj.finish_path()
                    self.define(path_obj)

    def modify_json(self):
        add_tex_to_json(self.global_tex_objs, False)
        return self

    def write_to_file(self, file_name):
        file_body = ET.ElementTree(self.root)
        file_body.write(file_name)
        modify_svg_file(file_name)

