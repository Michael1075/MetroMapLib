import re
import xml.etree.ElementTree as ElementTree

import maplib.constants as consts

from maplib.tools.assertions import assert_length
from maplib.tools.assertions import assert_type
from maplib.tools.simple_functions import modify_num
from maplib.tools.simple_functions import nums_to_string
from maplib.tools.simple_functions import string_to_nums
from maplib.tools.space_ops import get_simplified_direction
from maplib.utils.alignable import Alignable
from maplib.utils.color import Color
from maplib.utils.params_getter import Container


class ETElement(ElementTree.Element, Container):
    tag_name = ""
    attr_names = ()
    allow_append = True

    def __init__(self):
        Container.__init__(self)
        self.init_attrib_dict()
        ElementTree.Element.__init__(self, self.tag_name, attrib=self.attrib)

    def init_attrib_dict(self):
        self.attrib = {}
        return self


class Element(ETElement):
    def __init__(self, id_name):
        ETElement.__init__(self)
        self.init_id(id_name)
        self.init_attrs()

    def append(self, subelement):
        if not self.allow_append:
            raise NotImplementedError
        ETElement.append(self, subelement)
        if hasattr(subelement, "tex_objs"):
            if not hasattr(self, "tex_objs"):
                self.tex_objs = []
            self.tex_objs.extend(subelement.tex_objs)
        if hasattr(subelement, "template"):
            if not hasattr(self, "template"):
                self.init_template()
            self.template.append(subelement.template)
        return self

    def init_template(self):
        self.template = Group(None)
        return self

    def init_id(self, id_name):
        if id_name is not None:
            self.id_name = id_name
            self.set_attr_val("id", id_name)
        return self

    def init_attrs(self):
        pass

    @staticmethod
    def attr_val_to_str(val):
        if val is None:
            return "none"
        if isinstance(val, str):
            return val
        if isinstance(val, Style):
            return val.get_style_xml_str()
        if isinstance(val, float):
            return str(modify_num(val))
        raise TypeError(val)

    def set_attr_val(self, key, val):
        if key not in self.attr_names:
            raise NotImplementedError(key)
        self.attrib[key] = Element.attr_val_to_str(val)
        return self

    def set_style(self, style_dict):
        self.set_attr_val("style", Style(style_dict))
        return self


class Style(object):
    key_to_types_dict = {
        "fill": (Color, None, Element),
        "fill-opacity": (float,),
        "mask": (Element,),
        "stop-color": (Color, None),
        "stop-opacity": (float,),
        "stroke": (Color, None),
        "stroke-linecap": (str,),
        "stroke-linejoin": (str,),
        "stroke-opacity": (float,),
        "stroke-width": (float,),
    }

    def __init__(self, style_dict):
        self.style_dict = style_dict

    def get_style_xml_str(self):
        partial_strs = []
        for key, val in self.style_dict.items():
            val_str = self.get_val_str(key, val)
            partial_strs.append("{0}:{1}".format(key, val_str))
        return ";".join(partial_strs)

    def get_val_str(self, key, val):
        try:
            valid_types = self.key_to_types_dict[key]
        except KeyError:
            raise NotImplementedError(key)
        if val is None and None in valid_types:
            return "none"
        if isinstance(val, Color) and Color in valid_types:
            return val.hex_str()
        if isinstance(val, Element) and Element in valid_types:
            return "url(#{0})".format(val.id_name)
        if isinstance(val, float) and float in valid_types:
            return str(modify_num(val))
        if isinstance(val, str) and str in valid_types:
            return val
        raise TypeError(val)


class Svg(Element):
    tag_name = "svg"
    attr_names = ("version", "xmlns", "xmlns:xlink", "width", "height")

    def __init__(self):
        ETElement.__init__(self)
        self.init_attrs()

    def init_attrs(self):
        self.set_attr_val("version", self.params.SVG_VERSION)
        self.set_attr_val("xmlns", self.params.SVG_XMLNS)
        self.set_attr_val("xmlns:xlink", self.params.SVG_XLINK)
        self.set_attr_val("width", self.params.FULL_WIDTH)
        self.set_attr_val("height", self.params.FULL_HEIGHT)
        return self


class Defs(Element):
    tag_name = "defs"

    def __init__(self):
        ETElement.__init__(self)


class Group(Element):
    tag_name = "g"
    attr_names = ("id", "style", "transform")

    def use(self, href_id_name, relative_coord=None):
        use_obj = Use(href_id_name, relative_coord)
        self.append(use_obj)
        return self

    def use_with_style(self, href_id_name, style_dict, relative_coord=None):
        use_obj = Use(href_id_name, relative_coord)
        use_obj.set_style(style_dict)
        self.append(use_obj)
        return self

    def set_transform(self, prefix, transform_tuple):
        if prefix not in ("matrix", "translate", "scale"):
            raise NotImplementedError(prefix)
        for val in transform_tuple:
            assert_type(val, float)
        transform_str = "{0}({1})".format(prefix, nums_to_string(transform_tuple))
        self.set_attr_val("transform", transform_str)
        return self

    def matrix(self, matrix_tuple):
        """
        The transform matrix contains 6 elements, (a, b, c, d, e, f).
        x_viewport     a c e     x_userspace
        y_viewport  =  b d f  @  y_userspace
             1         0 0 1          1     
        """
        assert_length(matrix_tuple, 6)
        self.set_transform("matrix", matrix_tuple)
        return self

    def shift(self, shift_vector):
        assert_length(shift_vector, 2)
        self.set_transform("translate", shift_vector)
        return self

    def scale(self, scale_val):
        self.set_transform("scale", (scale_val,))
        return self

    def scale_and_shift(self, scale_val, shift_vector):
        assert_length(shift_vector, 2)
        matrix_tuple = (scale_val, 0., 0., scale_val, *shift_vector)
        self.matrix(matrix_tuple)
        return self

    def flip_y(self, scale_val=1.):
        matrix_tuple = (scale_val, 0., 0., -scale_val, 0., self.params.FULL_HEIGHT)
        self.matrix(matrix_tuple)
        return self


class Mask(Element):
    tag_name = "mask"
    attr_names = ("id", "maskUnits", "style")

    def use(self, href_id_name, relative_coord=None):
        use_obj = Use(href_id_name, relative_coord)
        self.append(use_obj)
        return self

    def use_with_style(self, href_id_name, style_dict, relative_coord=None):
        use_obj = Use(href_id_name, relative_coord)
        use_obj.set_style(style_dict)
        self.append(use_obj)
        return self


class Path(Element):
    tag_name = "path"
    attr_names = ("id", "d", "style")
    allow_append = False
    command_num_dict = {
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
    command_keys = list(command_num_dict.keys())

    def init_attrs(self):
        self.reset_path()
        return self

    def reset_path(self):
        self.path_strings = []
        self.set_attr_val("d", "")
        return self

    def add_path_command(self, command, *cmd_vals):
        assert_length(cmd_vals, Path.command_num_dict[command])
        if command != "M" and (not self.path_strings or self.path_strings[-1] == "Z"):
            raise ValueError(command)
        command_str = command + nums_to_string(cmd_vals)
        self.path_strings.append(command_str)
        return self

    def add_raw_command(self, command_str):
        pattern = "[{0}]".format("".join(Path.command_keys))
        pairs = list(zip(
            re.findall(pattern, command_str),
            re.split(pattern, command_str)[1:]
        ))
        for command, attr_val_str in pairs:
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
        7 attributes: rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y.
        rx & ry: lengths of semi-major axis and semi-minor axis;
        x_axis_rotation: the angle in degree included from the x-axis to
            the semi-major axis of the ellipse, which is positive if clockwise;
        large_arc_flag: 0 for minor arc, 1 for major arc;
        sweep_flag: 0 if the arc goes counter-clockwise from begin to end,
            while 1 if clockwise;
        x & y: the coordinate of end point.
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

    def __init__(self, href_id_name, relative_coord=None):
        ETElement.__init__(self)
        self.init_href_id_name(href_id_name)
        self.set_relative_coord(relative_coord)

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
        Alignable.__init__(self)
        Element.__init__(self, id_name)
        self.set_box_size(2 * radius * consts.RU)
        self.set_attr_val("r", radius)

    def align(self, aligned_point, aligned_direction=consts.ORIGIN):
        Alignable.align(self, aligned_point, aligned_direction)
        self.set_circle_center_point(self.get_critical_point(consts.ORIGIN))
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
        Alignable.__init__(self)
        Element.__init__(self, id_name)
        self.set_box_size(rect_size)
        width, height = rect_size
        self.set_attr_val("width", width)
        self.set_attr_val("height", height)

    def align(self, aligned_point, aligned_direction=consts.ORIGIN):
        Alignable.align(self, aligned_point, aligned_direction)
        self.set_rect_relative_coord(self.get_critical_point(consts.LD))
        return self

    def set_rect_relative_coord(self, relative_coord):
        x, y = relative_coord
        self.set_attr_val("x", x)
        self.set_attr_val("y", y)
        return self

    def set_corner_radius(self, rx, ry=None):
        if ry is None:
            ry = rx
        self.set_attr_val("rx", rx)
        self.set_attr_val("ry", ry)
        return self


class Stop(Element):
    tag_name = "stop"
    attr_names = ("offset", "style")
    allow_append = False

    def __init__(self, offset, stop_color, stop_opacity):
        ETElement.__init__(self)
        self.set_attr_val("offset", offset)
        self.set_style({
            "stop-color": stop_color,
            "stop-opacity": stop_opacity,
        })


class LinearGradient(Element):
    tag_name = "linearGradient"
    attr_names = ("id", "gradientUnits", "x1", "y1", "x2", "y2")

    def __init__(self, id_name, gradient_direction):
        self.gradient_direction = gradient_direction
        Element.__init__(self, id_name)
        self.init_attrs()

    def init_attrs(self):
        index_num = (get_simplified_direction(self.gradient_direction) + 4) // 2
        matrix_list = [0.] * 4
        matrix_list[index_num] = 1.
        for attr_name, matrix_val in zip(("x1", "y1", "x2", "y2"), matrix_list):
            self.set_attr_val(attr_name, matrix_val)
        return self

    def add_stop_color(self, offset, stop_color, stop_opacity):
        stop_color = Stop(offset, stop_color, stop_opacity)
        self.append(stop_color)
        return self

    def add_begin_color(self, color, opacity):
        self.add_stop_color(0., color, opacity)
        return self

    def add_end_color(self, color, opacity):
        self.add_stop_color(1., color, opacity)
