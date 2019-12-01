from functools import reduce
from xml.dom import minidom
import copy
import hashlib
import operator as op
import os

from maplib.constants import *
from maplib.parameters import *

from maplib.svg.svg_element import Group
from maplib.tools.config_ops import digest_locals
from maplib.tools.file_tools import get_global_file_dict
from maplib.tools.file_tools import get_global_path_dict
from maplib.tools.position import position
from maplib.tools.simple_functions import get_path_id_name
from maplib.tools.simple_functions import get_path_id_num
from maplib.tools.space_ops import get_positive_direction
from maplib.utils.alignable import Alignable


class TexFileWriter(object):
    def __init__(self, string, font_type):
        tex_string = "{{\\{0} {1}}}".format(font_type, string)
        new_body = TEMPLATE_TEX_FILE_BODY.replace(TEX_TO_REPLACE, tex_string)
        hash_val = self.tex_hash(new_body)
        digest_locals(self)

    def __str__(self):
        return self.hash_val

    def tex_hash(self, new_body):
        hasher = hashlib.sha256()
        hasher.update(new_body.encode())
        # Truncating at 16 bytes for cleanliness
        return hasher.hexdigest()[:16].upper()
    
    def generate_tex_file(self, svg_file_name):
        result = svg_file_name.replace(".svg", ".tex")
        if PRINT_TEX_WRITING_PROGRESS:
            print("Writing \"{0}\" to {1}".format(self.string, str(self)))
        with open(result, "w", encoding = "utf-8") as outfile:
            outfile.write(self.new_body)
        return result
    
    def tex_to_dvi(self, tex_file):
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
    
    def dvi_to_svg(self, dvi_file):
        """
        Converts a dvi, which potentially has multiple slides, into a
        directory full of enumerated pngs corresponding with these slides.
        Returns a list of PIL Image objects for these images sorted as they
        where in the dvi
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

    def tex_to_svg(self, file_name_body):
        svg_file_name = file_name_body + ".svg"
        tex_file = self.generate_tex_file(svg_file_name)
        dvi_file = self.tex_to_dvi(tex_file)
        svg_file = self.dvi_to_svg(dvi_file)
        for extension in (".tex", ".xdv", ".log", ".aux"):
            os.remove(file_name_body + extension)
        return svg_file

    def parse_svg_file(self, svg_file):
        tex_path_dict = dict()
        doc = minidom.parse(svg_file)
        viewbox = doc.getElementsByTagName("svg")[0].getAttribute("viewBox")
        viewbox_list = [float(val) for val in viewbox.split(" ")]
        paths = doc.getElementsByTagName("path")
        for path in paths:
            id_name = path.getAttribute("id")
            path_string = path.getAttribute("d")
            id_num = get_path_id_num(id_name)
            tex_path_dict[id_num] = path_string
        uses = doc.getElementsByTagName("use")
        href_num_list = []
        x_list = []
        y_list = []
        for use in uses:
            # Remove initial "#" character
            href_id_name = use.getAttribute("xlink:href")[1:]
            href_num = get_path_id_num(href_id_name)
            x = float(use.getAttribute("x"))
            y = float(use.getAttribute("y"))
            href_num_list.append(href_num)
            x_list.append(x)
            y_list.append(y)
        doc.unlink()
        os.remove(svg_file)
        tex_file_dict = {
            "v": viewbox_list,
            "h": href_num_list,
            "x": x_list,
            "y": y_list,
        }
        return (tex_file_dict, tex_path_dict)

    def get_dict_if_existed(self, use_current_data = True):
        global_file_dict = get_global_file_dict(use_current_data)
        font_file_dict = global_file_dict[self.font_type]
        if str(self) in font_file_dict.keys():
            return font_file_dict[str(self)]
        return None

    def write_tex_file(self, tex_file_dict, use_current_data = True):
        if tex_file_dict:
            global_path_dict = get_global_path_dict(use_current_data)
            font_path_dict = global_path_dict[self.font_type]
            tex_path_dict = {key: font_path_dict[key] for key in tex_file_dict["h"]}
        else:
            file_name_body = os.path.join(TEX_DIR, str(self))
            svg_file = self.tex_to_svg(file_name_body)
            tex_file_dict, tex_path_dict = self.parse_svg_file(svg_file)
        digest_locals(self, ("tex_file_dict", "tex_path_dict"))
        return self

    def write(self, use_current_data = False):
        tex_file_dict = self.get_dict_if_existed(use_current_data)
        self.write_tex_file(tex_file_dict, use_current_data)
        return self


class Tex(Alignable, TexFileWriter):
    def __init__(self, string, font_type, additional_scale_factor):
        self.additional_scale_factor = additional_scale_factor
        TexFileWriter.__init__(self, string, font_type)
        self.write()
        self.parse_dict()
        self.init_size_attrs()

    def parse_dict(self):
        tex_file_dict = self.tex_file_dict
        viewbox_list = tex_file_dict["v"]
        path_nums = tex_file_dict["h"]
        x_list = tex_file_dict["x"]
        y_list = tex_file_dict["y"]
        tex_paths_cmd_dict = dict()
        tex_uses_list = []
        for path_num, x, y in zip(path_nums, x_list, y_list):
            href_id_name = get_path_id_name(path_num, self.font_type)
            path_string = self.tex_path_dict[path_num]
            tex_paths_cmd_dict[href_id_name] = path_string
            relative_coord = position(x, y)
            tex_uses_list.append((href_id_name, relative_coord))
        digest_locals(self, ("viewbox_list", "tex_paths_cmd_dict", "tex_uses_list"))
        return self

    def init_size_attrs(self):
        scale_factor = TEX_BASE_SCALE_FACTOR * self.additional_scale_factor
        width = self.viewbox_list[2] * scale_factor
        height = self.viewbox_list[3] * scale_factor
        digest_locals(self)
        self.set_box_size(position(width, height))
        return self

    def compute_translate_tuple(self, aligned_point, aligned_direction):
        self.align(aligned_point, aligned_direction)
        x_min, y_min = self.viewbox_list[:2]
        x_prime, y_prime = self.get_critical_point(LD)
        y_prime = HEIGHT - self.height - y_prime
        return (x_prime - x_min * self.scale_factor, y_prime - y_min * self.scale_factor)
        

class TexBox(Alignable):
    def __init__(self, tex_objs, aligned_point, aligned_direction, buff, box_format):
        assert all([isinstance(tex_obj, Tex) for tex_obj in tex_objs])
        self.tex_objs = copy.copy(tex_objs)
        if box_format == VERTICAL:
            tex_objs.reverse()
        positive_direction = get_positive_direction(box_format)
        perpendicular_direction = RU - positive_direction
        box_size_list = [tex_obj.box_size for tex_obj in tex_objs]
        box_size = reduce(op.add, [
            np.max(box_size_list, axis = 0) * perpendicular_direction,
            np.sum(box_size_list, axis = 0) * positive_direction,
            (len(tex_objs) - 1) * buff * positive_direction
        ])
        self.set_box_size(box_size)
        self.align(aligned_point, aligned_direction)
        self.partial_aligned_direction = aligned_direction * perpendicular_direction - positive_direction
        major_aligned_point = self.get_critical_point(self.partial_aligned_direction)
        self.partial_aligned_points = [
            reduce(op.add, [
                major_aligned_point,
                np.sum(box_size_list[:k], axis = 0) * positive_direction,
                k * buff * positive_direction,
            ])
            for k in range(len(tex_objs))
        ]
        if box_format == VERTICAL:
            self.partial_aligned_points.reverse()


class TexGroup(Group):
    def __init__(self, id_name, group_objs):
        Group.__init__(self, id_name)
        self.group_objs = group_objs
        for group_obj in group_objs:
            self.append(group_obj)

    def construct_tex_partial_group(self, tex_obj, aligned_point, aligned_direction):
        scale_factor = tex_obj.scale_factor
        translate_tuple = tex_obj.compute_translate_tuple(aligned_point, aligned_direction)
        tex_partial_group = Group(None).scale(scale_factor, translate_tuple)
        for path_id, relative_coord in tex_obj.tex_uses_list:
            tex_partial_group.use(path_id, relative_coord)
        return tex_partial_group

    def append_tex_box(self, tex_box):
        for group_obj, tex_obj, partial_aligned_point in zip(
            self.group_objs, tex_box.tex_objs, tex_box.partial_aligned_points
        ):
            tex_partial_group = self.construct_tex_partial_group(
                tex_obj, partial_aligned_point, tex_box.partial_aligned_direction
            )
            group_obj.append(tex_partial_group)
        return self
    
