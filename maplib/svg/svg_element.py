import re
import xml.etree.ElementTree as ET

from maplib.parameters import *
from maplib.constants import *

from maplib.tools.assertions import is_number
from maplib.tools.simple_functions import modify_num
from maplib.tools.simple_functions import nums_to_string
from maplib.tools.simple_functions import string_to_nums
from maplib.utils.alignable import Alignable
from maplib.utils.style import Style


class ETElement(ET.Element):
    def __init__(self):
        ET.Element.__init__(self, self.tag_name, attrib = self.attrib)


class Element(ETElement):
    def __init__(self, id_name):
        self.init_attr_dict()
        self.init_id(id_name)
        self.init_attrs()
        ETElement.__init__(self)

    def append(self, subelement):
        if not self.allow_append:
            raise NotImplementedError
        ETElement.append(self, subelement)
        return self

    def attr_val_to_str(self, val):
        if val is None:
            return "none"
        if isinstance(val, Style):
            return val.get_style_xml_str()
        if is_number(val):
            return str(modify_num(val))
        if isinstance(val, str):
            return val
        raise TypeError

    def set_attr_val(self, key, val):
        if key not in self.attr_names:
            raise NotImplementedError
        self.attrib[key] = self.attr_val_to_str(val)
        return self

    def init_attr_dict(self):
        self.attrib = dict()
        return self

    def init_id(self, id_name):
        if id_name is not None:
            self.id_name = id_name
            self.set_attr_val("id", id_name)
        return self

    def init_attrs(self):
        pass

    def set_style(self, style_dict):
        self.set_attr_val("style", Style(style_dict))
        return self


class Svg(Element):
    tag_name = "svg"
    attr_names = ("version", "xmlns", "xmlns:xlink", "width", "height")
    allow_append = True

    def init_attrs(self):
        self.set_attr_val("version", SVG_VERSION)
        self.set_attr_val("xmlns", SVG_XMLNS)
        self.set_attr_val("xmlns:xlink", SVG_XLINK)
        self.set_attr_val("width", WIDTH)
        self.set_attr_val("height", HEIGHT)
        return self


class Defs(Element):
    tag_name = "defs"
    attr_names = tuple()
    allow_append = True


class Group(Element):
    tag_name = "g"
    attr_names = ("id", "style", "transform")
    allow_append = True

    def use(self, href_id_name, relative_coord = None):
        use_obj = Use(href_id_name, relative_coord)
        self.append(use_obj)
        return self

    def use_with_style(self, href_id_name, style_dict, relative_coord = None):
        use_obj = Use(href_id_name, relative_coord)
        use_obj.set_style(style_dict)
        self.append(use_obj)
        return self

    def set_transform(self, prefix, transform_tuple):
        assert prefix in ("matrix", "translate")
        transform_str = "{0}({1})".format(prefix, nums_to_string(transform_tuple))
        self.set_attr_val("transform", transform_str)
        return self

    def matrix(self, matrix_tuple):
        """
        The transform matrix contains 6 elements, (a, b, c, d, e, f)
        x_viewport     a c e     x_userspace
        y_viewport  =  b d f  @  y_userspace
             1         0 0 1          1     
        """
        assert len(matrix_tuple) == 6
        self.set_transform("matrix", matrix_tuple)
        return self

    def translate(self, translate_tuple):
        assert len(translate_tuple) == 2
        self.set_transform("translate", translate_tuple)
        return self

    def scale(self, scale_val):
        matrix_tuple = (scale_val, 0, 0, scale_val, 0, 0)
        self.matrix(matrix_tuple)
        return self

    def flip_y(self, scale_val = 1.0):
        matrix_tuple = (scale_val, 0, 0, -scale_val, 0, HEIGHT)
        self.matrix(matrix_tuple)
        return self

    def flip_y_for_tex(self):
        self.flip_y(TEX_BASE_SCALE_FACTOR)
        return self


class Mask(Element):
    tag_name = "mask"
    attr_names = ("id", "maskUnits", "style")
    allow_append = True

    def init_attrs(self):
        self.set_attr_val("maskUnits", "userSpaceOnUse")
        return self

    def use(self, href_id_name, relative_coord = None):
        return Group.use(self, href_id_name, relative_coord)

    def use_with_style(self, href_id_name, style_dict, relative_coord = None):
        return Group.use_with_style(self, href_id_name, style_dict, relative_coord)


class Path(Element):
    tag_name = "path"
    attr_names = ("id", "d", "style")
    allow_append = False

    def init_attrs(self):
        self.command_num_dict = {
            "M": 2,  # moveto
            "L": 2,  # lineto
            "H": 1,  # horizontal lineto
            "V": 1,  # vertical lineto
            "C": 6,  # curveto
            "S": 4,  # smooth curveto
            "Q": 4,  # quadratic Bezier curve
            "T": 2,  # smooth quadratic Bezier curveto
            "A": 7,  # elliptical Arc
            "Z": 0,  # closepath
        }
        self.command_keys = list(self.command_num_dict.keys())
        self.reset_path()
        return self

    def reset_path(self):
        self.path_strings = []
        self.set_attr_val("d", "")
        return self

    def add_path_command(self, command, *cmd_vals):
        assert len(cmd_vals) == self.command_num_dict[command]
        assert command == "M" or self.path_strings
        command_str = command + nums_to_string(cmd_vals)
        self.path_strings.append(command_str)
        return self

    def add_raw_command(self, command_str):
        pattern = "[{0}]".format("".join(self.command_keys))
        pairs = list(zip(
            re.findall(pattern, command_str),
            re.split(pattern, command_str)[1:]
        ))
        for command, attr_val_str in pairs:
            if self.command_num_dict[command] == 0:
                self.add_path_command(command)
            else:
                cmd_vals = string_to_nums(attr_val_str)
                self.add_path_command(command, *cmd_vals)
        return self

    def add_element_path(self, element):
        raw_command = element.get_path_string()
        self.add_raw_command(raw_command)
        self.finish_path()
        return self

    def move_to(self, coord):
        self.add_path_command("M", *coord)
        return self

    def line_to(self, coord):
        self.add_path_command("L", *coord)
        return self

    def h_line_to(self, x):
        self.add_path_command("H", x)
        return self

    def v_line_to(self, y):
        self.add_path_command("V", y)
        return self

    def arc_to(self, coord, radius, large_arc_flag, sweep_flag):
        """
        7 attributes: rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y
        rx, ry: lengths of semi-major axis and semi-minor axis
        x_axis_rotation: the angle in degree included from the x-axis to semi-major axis of the ellipse,
            which is positive if clockwise
        large_arc_flag: 0 for minor arc, 1 for major arc
        sweep_flag: 0 if the arc goes counter-clockwise from begin to end,
            while 1 if clockwise
        x, y: the coordinate of end point
        """
        rx = ry = radius
        x_axis_rotation = 0
        x, y = coord
        self.add_path_command("A", rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y)
        return self

    def close_path(self):
        self.add_path_command("Z")
        return self

    def get_path_string(self):
        return "".join(self.path_strings)

    def finish_path(self):
        self.set_attr_val("d", self.get_path_string())
        return self


class Use(Element):
    tag_name = "use"
    attr_names = ("xlink:href", "x", "y", "style")
    allow_append = False

    def __init__(self, href_id_name, relative_coord = None):
        self.init_attr_dict()
        self.init_href_id_name(href_id_name)
        self.set_relative_coord(relative_coord)
        ETElement.__init__(self)

    def init_href_id_name(self, href_id_name):
        self.set_attr_val("xlink:href", "#" + href_id_name)
        return self

    def set_relative_coord(self, relative_coord):
        if relative_coord is not None:
            x, y = relative_coord
            self.set_attr_val("x", x)
            self.set_attr_val("y", y)
        return self


class Circle(Alignable, Element):
    tag_name = "circle"
    attr_names = ("id", "r", "cx", "cy", "style")
    allow_append = False

    def __init__(self, id_name, radius):
        Element.__init__(self, id_name)
        self.set_box_size(2 * radius * RU)
        self.set_attr_val("r", radius)
        return self

    def align(self, aligned_point, aligned_direction = ORIGIN):
        Alignable.align(self, aligned_point, aligned_direction)
        self.set_circle_center_point(self.center_point)
        return self

    def set_circle_center_point(self, center_point):
        cx, cy = center_point
        self.set_attr_val("cx", cx)
        self.set_attr_val("cy", cy)
        return self


class Rectangle(Alignable, Element):
    tag_name = "rect"
    attr_names = ("id", "width", "height", "x", "y", "rx", "ry", "style")
    allow_append = False

    def __init__(self, id_name, rect_size):
        Element.__init__(self, id_name)
        self.set_box_size(rect_size)
        width, height = rect_size
        self.set_attr_val("width", width)
        self.set_attr_val("height", height)
        return self

    def align(self, aligned_point, aligned_direction = ORIGIN):
        self.center_point = aligned_point - aligned_direction * self.semi_box_size
        relative_coord = self.center_point + LD * self.semi_box_size
        self.set_rect_relative_coord(relative_coord)
        return self

    def set_rect_relative_coord(self, relative_coord):
        x, y = relative_coord
        self.set_attr_val("x", x)
        self.set_attr_val("y", y)
        return self

    def set_corner_radius(self, rx, ry = None):
        if ry is None:
            ry = rx
        self.set_attr_val("rx", rx)
        self.set_attr_val("ry", ry)
        return self

