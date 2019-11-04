from xml.dom import minidom
import os

from constants import *
from parameters import *

from tools.config_ops import digest_locals
from tools.position import position
from tools.tex_file_writing import tex_to_svg_file


class Tex(object):
    def __init__(self, string, font_cmds, added_scale_factor):
        assert isinstance(string, str)
        tex_string = "{{{0} {1}}}".format(
            " ".join([("\\" + cmd) for cmd in font_cmds]),
            string
        )
        font_type = "_".join(font_cmds)
        self.font_type = font_type
        svg_file = tex_to_svg_file(tex_string, font_type)
        self.parse_svg_file(svg_file)
        self.init_size_attrs(added_scale_factor)

    def parse_svg_file(self, svg_file):
        doc = minidom.parse(svg_file)
        viewbox = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
        viewbox_tuple = tuple([float(val) for val in viewbox.split(" ")])
        tex_paths_dict = dict()
        paths = doc.getElementsByTagName("path")
        for path in paths:
            id_name = path.getAttribute("id")
            path_string = path.getAttribute("d")
            tex_paths_dict.update({id_name: path_string})
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
        digest_locals(self, ("viewbox_tuple", "tex_paths_dict", "tex_uses_list"))
        return self

    def init_size_attrs(self, added_scale_factor):
        scale_factor = TEX_BASE_SCALE_FACTOR * added_scale_factor
        width = self.viewbox_tuple[2] * scale_factor
        height = self.viewbox_tuple[3] * scale_factor
        box_size = position(width, height)
        digest_locals(self)
        return self

    def compute_translate_tuple(self, aligned_point, aligned_direction):
        digest_locals(self)
        x_min, y_min = self.viewbox_tuple[:2]
        x_prime, y_prime = self.get_critical_point(LD)
        y_prime = HEIGHT - self.height - y_prime
        return (x_prime / self.scale_factor - x_min, y_prime / self.scale_factor - y_min)

    def get_critical_point(self, direction):
        center_point = self.aligned_point - self.aligned_direction * self.box_size / 2
        return center_point + direction * self.box_size / 2


class TexBox(object):
    def __init__(self, tex_objs, aligned_point, aligned_direction, line_buff):
        assert all([isinstance(tex_obj, Tex) for tex_obj in tex_objs])
        total_height = sum([tex_obj.height for tex_obj in tex_objs]) + (len(tex_objs) - 1) * line_buff
        top_aligned_point = aligned_point + (1 - aligned_direction[1]) * total_height * UP / 2
        partial_aligned_points = [
            (top_aligned_point + (sum([tex_obj.height for tex_obj in tex_objs[:k]]) + k * line_buff) * DOWN)
            for k in range(len(tex_objs))
        ]
        partial_aligned_direction = aligned_direction * RIGHT + UP
        digest_locals(self, ("tex_objs", "partial_aligned_points", "partial_aligned_direction"))

    def __len__(self):
        return len(self.tex_objs)
    
