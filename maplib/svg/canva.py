import xml.etree.ElementTree as ET

from maplib.svg.svg_element import Defs
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Svg
from maplib.tools.svg_file_tools import modify_svg_file


class Canva(object):
    def __init__(self, file_name):
        self.init_background()
        self.init_tex_path_id_set()
        self.construct()
        self.write_to_file(file_name)

    def construct(self):
        """
        Implemented in subclasses
        """
        pass

    def init_background(self):
        self.root = Svg()
        self.defs = Defs()
        self.root.append(self.defs)
        self.canva = Group().flip_y()
        self.root.append(self.canva)

    def init_tex_path_id_set(self):
        self.global_tex_path_id_set = set()

    def define(self, component):
        self.defs.append(component)

    def define_tex(self, component):
        self.define_path_from_dict(component.tex_paths_dict)
        self.define(component)

    def draw(self, id_name):
        self.canva.use(id_name)

    def define_path_from_dict(self, tex_paths_dict):
        for path_id, path_obj in tex_paths_dict.items():
            if path_id not in self.global_tex_path_id_set:
                self.global_tex_path_id_set.add(path_id)
                self.define(path_obj)

    def write_to_file(self, file_name):
        file_body = ET.ElementTree(self.root)
        file_body.write(file_name)
        modify_svg_file(file_name)

