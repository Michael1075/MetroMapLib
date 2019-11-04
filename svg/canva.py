import xml.etree.ElementTree as ET

from parameters import TEX_BASE_SCALE_FACTOR
from parameters import TEX_FONT_CMDS

from svg.svg_element import Defs
from svg.svg_element import Group
from svg.svg_element import Path
from svg.svg_element import Svg
from svg.svg_element import Use
from tools.svg_file_tools import modify_svg_file


class Canva(object):
    def __init__(self, file_name):
        self.root = Svg()
        self.defs = Defs()
        self.root.append(self.defs)
        self.canva = Group().flip_y()
        self.root.append(self.canva)
        self.init_tex_group()
        self.construct()
        self.append_tex_group()
        self.write_to_file(file_name)

    def construct(self):
        """
        Implemented in subclasses
        """
        pass

    def init_tex_group(self):
        self.base_tex_group = Group().flip_y(TEX_BASE_SCALE_FACTOR)

    def append_tex_group(self):
        self.canva.append(self.base_tex_group)

    def define(self, component):
        self.defs.append(component)

    def draw(self, *href_id_names):
        for id_name in href_id_names:
            self.canva.use(id_name)

    def write_tex(self, *href_id_names):
        for id_name in href_id_names:
            self.base_tex_group.use(id_name)

    def construct_tex_group(self, tex_obj, aligned_point, aligned_direction):
        path_id_rename_dict = dict()
        for path_id in tex_obj.tex_paths_dict.keys():
            new_path_id = "g" + str(TEX_FONT_CMDS.index(tex_obj.font_type)) + path_id[path_id.index("-"):]
            path_id_rename_dict[path_id] = new_path_id
            if new_path_id not in self.tex_path_id_set:
                self.tex_path_id_set.add(new_path_id)
                path_obj = Path(new_path_id)
                path_obj.add_raw_command(tex_obj.tex_paths_dict[path_id])
                path_obj.finish_path()
                self.define(path_obj)
        translate_tuple = tex_obj.compute_translate_tuple(aligned_point, aligned_direction)
        tex_group = Group().translate(translate_tuple)
        for path_id, relative_coord in tex_obj.tex_uses_list:
            tex_group.use(path_id_rename_dict[path_id], relative_coord)
        return tex_group

    def append_tex_box_to_groups_seperately(self, tex_objs, tex_box, group_objs):
        assert len(tex_objs) == len(tex_box) == len(group_objs)
        for group_obj, tex_obj, real_aligned_point in zip(group_objs, tex_objs, tex_box.partial_aligned_points):
            tex_group = self.construct_tex_group(tex_obj, real_aligned_point, tex_box.partial_aligned_direction)
            group_obj.append(tex_group)

    def write_to_file(self, file_name):
        file_body = ET.ElementTree(self.root)
        file_body.write(file_name)
        modify_svg_file(file_name)

