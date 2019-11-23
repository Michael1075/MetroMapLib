from xml.dom import minidom
import os

from maplib.constants import *
from maplib.parameters import *

from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Path
from maplib.tools.config_ops import digest_locals
from maplib.tools.position import position
from maplib.tools.tex_file_writing import tex_hash
from maplib.tools.tex_file_writing import tex_to_svg
from maplib.utils.alignable import Alignable


class PureTex(object):
    def __init__(self, string, font_type):
        assert isinstance(string, str)
        tex_string = "{{\\{0} {1}}}".format(font_type, string)
        new_body = TEMPLATE_TEX_FILE_BODY.replace(TEX_TO_REPLACE, tex_string)
        file_name_body = os.path.join(TEX_DIR, font_type, tex_hash(new_body))
        digest_locals(self)

    def tex_to_svg_file(self):
        return tex_to_svg(self.new_body, self.file_name_body)


class Tex(PureTex, Alignable):
    def __init__(self, string, font_type, added_scale_factor):
        PureTex.__init__(self, string, font_type)
        svg_file = self.tex_to_svg_file()
        self.parse_svg_file(svg_file)
        self.init_size_attrs(added_scale_factor)

    def parse_svg_file(self, svg_file):
        doc = minidom.parse(svg_file)
        viewbox = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
        viewbox_tuple = tuple([float(val) for val in viewbox.split(" ")])
        tex_paths_cmd_dict = dict()
        paths = doc.getElementsByTagName("path")
        for path in paths:
            id_name = path.getAttribute("id")
            path_string = path.getAttribute("d")
            tex_paths_cmd_dict[id_name] = path_string
        tex_uses_list = []
        uses = doc.getElementsByTagName("use")
        for use in uses:
            # Remove initial "#" character
            href_id_name = use.getAttribute("xlink:href")[1:]
            x = float(use.getAttribute("x"))
            y = float(use.getAttribute("y"))
            relative_coord = position(x, y)
            tex_uses_list.append((href_id_name, relative_coord))
        doc.unlink()
        digest_locals(self, ("viewbox_tuple", "tex_paths_cmd_dict", "tex_uses_list"))
        return self

    def init_size_attrs(self, added_scale_factor):
        scale_factor = TEX_BASE_SCALE_FACTOR * added_scale_factor
        width = self.viewbox_tuple[2] * scale_factor
        height = self.viewbox_tuple[3] * scale_factor
        digest_locals(self)
        self.set_box_size(position(width, height))
        return self

    def compute_translate_tuple(self, aligned_point, aligned_direction):
        self.align(aligned_point, aligned_direction)
        x_min, y_min = self.viewbox_tuple[:2]
        x_prime, y_prime = self.get_critical_point(LD)
        y_prime = HEIGHT - self.height - y_prime
        return (x_prime / self.scale_factor - x_min, y_prime / self.scale_factor - y_min)


class TexBox(Alignable):
    def __init__(self, tex_objs, aligned_point, aligned_direction, line_buff):
        assert all([isinstance(tex_obj, Tex) for tex_obj in tex_objs])
        self.tex_objs = tex_objs
        width = max([tex_obj.width for tex_obj in tex_objs])
        height = sum([tex_obj.height for tex_obj in tex_objs]) + (len(tex_objs) - 1) * line_buff
        self.set_box_size(position(width, height))
        self.align(aligned_point, aligned_direction)
        self.partial_aligned_direction = aligned_direction * RIGHT + UP
        top_aligned_point = self.get_critical_point(self.partial_aligned_direction)
        self.partial_aligned_points = [
            (top_aligned_point + (sum([tex_obj.height for tex_obj in tex_objs[:k]]) + k * line_buff) * DOWN)
            for k in range(len(tex_objs))
        ]


class TexGroup(Group):
    def __init__(self, id_name, group_objs):
        Group.__init__(self, id_name)
        self.tex_paths_dict = dict()
        self.group_objs = group_objs
        for group_obj in group_objs:
            self.append(group_obj)

    def construct_tex_partial_group(self, tex_obj, aligned_point, aligned_direction):
        path_id_rename_dict = dict()
        for path_id, path_cmd in tex_obj.tex_paths_cmd_dict.items():
            new_path_id = "g" + str(TEX_FONT_CMDS.index(tex_obj.font_type)) + path_id[path_id.index("-"):]
            path_id_rename_dict[path_id] = new_path_id
            if new_path_id not in self.tex_paths_dict.keys():
                path_obj = Path(new_path_id)
                path_obj.add_raw_command(path_cmd)
                path_obj.finish_path()
                self.tex_paths_dict[new_path_id] = path_obj
        translate_tuple = tex_obj.compute_translate_tuple(aligned_point, aligned_direction)
        tex_partial_group = Group(None).translate(translate_tuple)
        for path_id, relative_coord in tex_obj.tex_uses_list:
            tex_partial_group.use(path_id_rename_dict[path_id], relative_coord)
        return tex_partial_group

    def append_tex_box(self, tex_box):
        for group_obj, tex_obj, partial_aligned_point in zip(self.group_objs, tex_box.tex_objs, tex_box.partial_aligned_points):
            tex_partial_group = self.construct_tex_partial_group(tex_obj, partial_aligned_point, tex_box.partial_aligned_direction)
            group_obj.append(tex_partial_group)
        return self
    
