from functools import reduce
from xml.dom import minidom
import numpy as np
import operator as op
import os

import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.svg_element import Group
from maplib.tools.assertions import assert_type
from maplib.tools.file_tools import get_global_file_dict
from maplib.tools.file_tools import get_global_path_dict
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.simple_functions import get_path_id_name
from maplib.tools.simple_functions import get_path_id_num_str
from maplib.tools.simple_functions import nums_to_string
from maplib.tools.simple_functions import remove_list_redundancies
from maplib.tools.simple_functions import string_to_nums
from maplib.tools.space_ops import get_positive_direction
from maplib.utils.alignable import Alignable


class TexFileBaseWriter(object):
    """
    Inspired by 3b1b/manim.
    """
    def __init__(self, string, font_type, tex_string):
        new_body = params.TEMPLATE_TEX_FILE_BODY.replace(params.TEX_TO_REPLACE, tex_string)
        self.tex_string = tex_string
        self.new_body = new_body
        file_name_body = os.path.join(params.TEX_CACHE_DIR, font_type + string)
        svg_file_name = file_name_body + ".svg"
        tex_file = self.generate_tex_file(svg_file_name)
        dvi_file = TexFileBaseWriter.tex_to_dvi(tex_file)
        self.svg_file = TexFileBaseWriter.dvi_to_svg(dvi_file)
        for extension in (".tex", ".xdv", ".log", ".aux"):
            os.remove(file_name_body + extension)

    def generate_tex_file(self, svg_file_name):
        result = svg_file_name.replace(".svg", ".tex")
        if params.PRINT_TEX_WRITING_PROGRESS_MSG:
            print(params.TEX_WRITING_PROGRESS_MSG.format(self.tex_string))
        with open(result, "w", encoding=consts.UTF_8) as outfile:
            outfile.write(self.new_body)
        return result
    
    @staticmethod
    def tex_to_dvi(tex_file):
        result = tex_file.replace(".tex", ".xdv")
        file_dir = os.path.dirname(tex_file)
        commands = [
            "xelatex",
            "-no-pdf",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=" + file_dir,
            tex_file,
            ">",
            os.devnull
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            raise OSError
        return result
    
    @staticmethod
    def dvi_to_svg(dvi_file):
        """
        Converts a dvi, which potentially has multiple slides, into a
        directory full of enumerated pngs corresponding with these slides.
        Returns a list of PIL Image objects for these images sorted as they
        where in the dvi.
        """
        result = dvi_file.replace(".xdv", ".svg")
        commands = [
            "dvisvgm",
            dvi_file,
            "-n",
            "-v",
            "0",
            "-o",
            result,
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
        return result


class TexFileWriter(object):
    def __init__(self, string, font_type):
        assert_type(string, str)
        if font_type not in params.TEX_FONT_CMDS:
            raise ValueError(font_type)
        self.string = string
        self.font_type = font_type
        self.tex_string = "{{\\{0} {1}}}".format(font_type, string)

    def __eq__(self, obj):
        return reduce(op.and_, [
            isinstance(obj, TexFileWriter),
            self.tex_string == obj.tex_string,
        ])

    def __hash__(self):
        return hash(self.tex_string)

    @staticmethod
    def tex_file_dict_to_lists(tex_file_dict):
        viewbox_list_str = tex_file_dict["v"]
        href_num_list_str = tex_file_dict["h"]
        x_list_str = tex_file_dict["x"]
        y_list_str = tex_file_dict["y"]
        viewbox_list = string_to_nums(viewbox_list_str)
        href_num_list = href_num_list_str.split()
        tex_length = len(href_num_list)
        if isinstance(x_list_str, float):
            x_list = [x_list_str] * tex_length
        else:
            x_list = string_to_nums(x_list_str)
        if isinstance(y_list_str, float):
            y_list = [y_list_str] * tex_length
        else:
            y_list = string_to_nums(y_list_str)
        return viewbox_list, href_num_list, x_list, y_list
    
    @staticmethod
    def tex_file_lists_to_dict(viewbox_list, href_num_list, x_list, y_list):
        viewbox_list_str = nums_to_string(viewbox_list)
        href_num_list_str = " ".join(href_num_list)
        if len(remove_list_redundancies(x_list)) == 1:
            x_list_str = x_list[0]
        else:
            x_list_str = nums_to_string(x_list)
        if len(remove_list_redundancies(y_list)) == 1:
            y_list_str = y_list[0]
        else:
            y_list_str = nums_to_string(y_list)
        return {
            "v": viewbox_list_str,
            "h": href_num_list_str,
            "x": x_list_str,
            "y": y_list_str,
        }

    @staticmethod
    def parse_svg_file(svg_file):
        tex_path_dict = {}
        doc = minidom.parse(svg_file)
        viewbox = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
        viewbox_list = string_to_nums(viewbox)
        paths = doc.getElementsByTagName("path")
        for path in paths:
            id_name = path.getAttribute("id")
            path_string = path.getAttribute("d")
            id_num = get_path_id_num_str(id_name)
            tex_path_dict[id_num] = path_string
        uses = doc.getElementsByTagName("use")
        href_num_list = []
        x_list = []
        y_list = []
        for use in uses:
            # Remove initial "#" character.
            href_id_name = use.getAttribute("xlink:href")[1:]
            href_num = get_path_id_num_str(href_id_name)
            x = float(use.getAttribute("x"))
            y = float(use.getAttribute("y"))
            href_num_list.append(href_num)
            x_list.append(x)
            y_list.append(y)
        doc.unlink()
        os.remove(svg_file)
        tex_file_dict = TexFileWriter.tex_file_lists_to_dict(viewbox_list, href_num_list, x_list, y_list)
        return tex_file_dict, tex_path_dict

    def get_dict_if_existed(self, use_current_data=False):
        global_file_dict = get_global_file_dict(use_current_data)
        font_file_dict = global_file_dict[self.font_type]
        if self.string in font_file_dict.keys():
            return font_file_dict[self.string]
        return None

    def write_tex_file(self, tex_file_dict):
        if tex_file_dict:
            global_path_dict = get_global_path_dict()
            font_path_dict = global_path_dict[self.font_type]
            href_num_list = tex_file_dict["h"].split()
            tex_path_dict = {key: font_path_dict[key] for key in href_num_list}
        else:
            svg_file = TexFileBaseWriter(self.string, self.font_type, self.tex_string).svg_file
            tex_file_dict, tex_path_dict = TexFileWriter.parse_svg_file(svg_file)
        self.tex_file_dict = tex_file_dict
        self.tex_path_dict = tex_path_dict
        return self

    def write_directly(self):
        tex_file_dict = self.get_dict_if_existed()
        self.write_tex_file(tex_file_dict)
        return self


class Tex(Alignable, TexFileWriter):
    def __init__(self, string, font_type, additional_scale_factor):
        self.additional_scale_factor = additional_scale_factor
        TexFileWriter.__init__(self, string, font_type)
        self.write_directly()
        self.parse_dict()
        self.init_size_attrs()

    def parse_dict(self):
        viewbox_list, href_num_list, x_list, y_list = TexFileWriter.tex_file_dict_to_lists(self.tex_file_dict)
        tex_paths_cmd_dict = {}
        tex_uses_list = []
        for path_id_num, x, y in zip(href_num_list, x_list, y_list):
            href_id_name = get_path_id_name(path_id_num, self.font_type)
            path_string = self.tex_path_dict[path_id_num]
            tex_paths_cmd_dict[href_id_name] = path_string
            relative_coord = np_float(x, y)
            tex_uses_list.append((href_id_name, relative_coord))
        self.viewbox_list = viewbox_list
        self.tex_paths_cmd_dict = tex_paths_cmd_dict
        self.tex_uses_list = tex_uses_list
        return self

    def init_size_attrs(self):
        scale_factor = params.TEX_BASE_SCALE_FACTOR * self.additional_scale_factor
        width = self.viewbox_list[2] * scale_factor
        height = self.viewbox_list[3] * scale_factor
        self.scale_factor = scale_factor
        self.height = height
        self.set_box_size(np_float(width, height))
        return self

    def compute_shift_vector(self, aligned_point, aligned_direction):
        self.align(aligned_point, aligned_direction)
        x_min, y_min = self.viewbox_list[:2]
        x_prime, y_prime = self.get_critical_point(consts.LD)
        y_prime = params.FULL_HEIGHT - self.height - y_prime
        return x_prime - x_min * self.scale_factor, y_prime - y_min * self.scale_factor
        

class TexBox(Alignable):
    def __init__(self, tex_objs, aligned_point, aligned_direction, buff, box_format):
        for tex_obj in tex_objs:
            assert_type(tex_obj, Tex)
        self.tex_objs = tex_objs.copy()
        if box_format == consts.VERTICAL:
            tex_objs.reverse()
        positive_direction = get_positive_direction(box_format)
        perpendicular_direction = consts.RU - positive_direction
        box_size_list = [tex_obj.box_size for tex_obj in tex_objs]
        box_size = reduce(op.add, [
            np.max(box_size_list, axis=0) * perpendicular_direction,
            np.sum(box_size_list, axis=0) * positive_direction,
            (len(tex_objs) - 1) * buff * positive_direction
        ])
        self.set_box_size(box_size)
        self.align(aligned_point, aligned_direction)
        self.partial_aligned_direction = aligned_direction * perpendicular_direction - positive_direction
        major_aligned_point = self.get_critical_point(self.partial_aligned_direction)
        self.partial_aligned_points = [
            reduce(op.add, [
                major_aligned_point,
                np.sum(box_size_list[:k], axis=0) * positive_direction,
                k * buff * positive_direction,
            ])
            for k in range(len(tex_objs))
        ]
        if box_format == consts.VERTICAL:
            self.partial_aligned_points.reverse()


class TexGroup(Group):
    def __init__(self, id_name, group_objs):
        Group.__init__(self, id_name)
        self.group_objs = group_objs
        for group_obj in group_objs:
            self.append(group_obj)

    @staticmethod
    def construct_tex_partial_group(tex_obj, aligned_point, aligned_direction):
        scale_factor = tex_obj.scale_factor
        shift_vector = tex_obj.compute_shift_vector(aligned_point, aligned_direction)
        tex_partial_group = Group(None).scale_and_shift(scale_factor, shift_vector)
        for path_id, relative_coord in tex_obj.tex_uses_list:
            tex_partial_group.use(path_id, relative_coord)
        return tex_partial_group

    def append_tex_box(self, tex_box):
        for group_obj, tex_obj, partial_aligned_point in zip(
            self.group_objs, tex_box.tex_objs, tex_box.partial_aligned_points
        ):
            tex_partial_group = TexGroup.construct_tex_partial_group(
                tex_obj, partial_aligned_point, tex_box.partial_aligned_direction
            )
            group_obj.append(tex_partial_group)
        return self
