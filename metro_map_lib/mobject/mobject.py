from functools import reduce
import cairo
import numpy as np
import operator as op

from attributes import *

from constants import *

from tools.assertions import is_2D_data

from tools.config_ops import digest_config
from tools.config_ops import digest_locals

from tools.simple_functions import get_color_rgb
from tools.simple_functions import modify_point
from tools.simple_functions import unit_to_point

from tools.space_ops import abs_arg_pair
from tools.space_ops import abs_C
from tools.space_ops import arg_C
from tools.space_ops import arg_principle
from tools.space_ops import flip_about_x_axis
from tools.space_ops import shift


class Mobject(object):
    """
    Get components if hasattr(self, "components"),
    otherwise call the on_draw method when drawing.
    All components must be type Mobject.
    """
    CONFIG = {
        "layer": 0,
        "stroke_width": 0.0,
        "stroke_color": BLACK,
        "stroke_opacity": 1.0,
        "fill_color": None,
        "fill_opacity": 1.0,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)

    def generate(self, ctx, size):
        pass

    def on_draw(self, ctx, size):
        ctx.new_path()
        ctx.set_source_rgba(*get_color_rgb(self.stroke_color), self.stroke_opacity)
        ctx.set_line_width(unit_to_point(self.stroke_width))
        ctx = self.generate(ctx, size)
        ctx.stroke_preserve()
        if self.fill_color is not None:
            ctx.set_source_rgba(*get_color_rgb(self.fill_color), self.fill_opacity)
            ctx.fill_preserve()
        ctx.close_path()
        return ctx


class Line(Mobject):
    CONFIG = {
        "stroke_width": 1.0,
    }

    def __init__(self, start_point, end_point, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        assert is_2D_data(start_point, end_point)

    def generate(self, ctx, size):
        ctx.move_to(*unit_to_point(modify_point(self.start_point, size)))
        ctx.line_to(*unit_to_point(modify_point(self.end_point, size)))
        return ctx


class Arc(Mobject):
    CONFIG = {
        "arc_center": ORIGIN,
        "radius": 1,
        "start_angle": 0,
        "angle": PI / 2,
        "stroke_width": 1.0,
    }

    def __init__(self, **kwargs):
        Mobject.__init__(self, **kwargs)

    def generate(self, ctx, size):
        angle1 = -self.start_angle
        angle2 = angle1 - self.angle
        if self.angle >= 0:
            arc_func = ctx.arc_negative
        else:
            arc_func = ctx.arc
        arc_func(
            *unit_to_point(modify_point(self.arc_center, size)),
            unit_to_point(self.radius),
            angle1,
            angle2
        )
        return ctx


class ArcBetweenPoints(Arc):
    def __init__(self, start_point, end_point, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        assert is_2D_data(start_point, end_point)
        arc_center, radius, start_angle = self.get_stuff()
        Arc.__init__(
            self,
            arc_center = arc_center,
            radius = radius,
            start_angle = start_angle,
            **kwargs
        )

    def get_stuff(self):
        angle = arg_principle(self.angle)
        assert angle != 0
        vec = self.end_point - self.start_point
        radius = abs_C(vec / 2) / abs(np.sin(angle / 2))
        argument = arg_C(vec) + (PI - angle) / 2
        if angle < 0:
            argument -= PI
        arc_center = shift(abs_arg_pair(radius, argument), self.start_point)
        start_angle = arg_principle(argument + PI)
        return (arc_center, radius, start_angle)


class Circle(Arc):
    CONFIG = {
        "start_angle": 0,
        "angle": TAU,
    }


class TextPartial(Mobject):
    CONFIG = {
        "aligned_direction": ORIGIN,
        "aligned_point_coord": ORIGIN,
        "font_size": 1.0,
        "font_face": "Sans",
        "font_slant": 0,
        "font_weight": 0,
    }

    def __init__(self, text, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.init_height()

    def font_to_height(self, font_size):
        return (font_size * 1.0)

    def init_height(self):
        self.height = self.font_to_height(self.font_size)
        return self

    def get_control_point_and_direction(self):
        """
        Control point is the point where
        the vertical line, where aligned_point_coord lies,
        and the horizontal line, which bounds the text object at the top,
        intersects, which is set in order to align the text more conveniently.
        Control direction is one of (LEFT, ORIGIN, RIGHT),
        which depends on aligned_direction.
        """
        x, y = self.aligned_direction
        distance_to_top = ((1 - y) / 2) * self.height
        control_point = shift(self.aligned_point_coord, distance_to_top * UP)
        control_direction = np.array([x, 0])
        return (control_point, control_direction)

    def generate(self, ctx, size):
        ctx.set_font_size(unit_to_point(self.font_size))
        ctx.select_font_face(self.font_face, self.font_slant, self.font_weight)
        ctx.move_to(*self.get_move_to_point(ctx, size))
        ctx.show_text(self.text)
        return ctx

    def get_move_to_point(self, ctx, size):
        control_point, control_direction = self.get_control_point_and_direction()
        x_bearing, y_bearing, width, height, x_advance, y_advance = ctx.text_extents(self.text)
        point = (control_direction + UP + RU) * np.array([width, height]) / 2
        point = flip_about_x_axis(point)
        point = shift(point, height * UP)
        point = shift(point, np.array([x_bearing, y_bearing]))
        point = unit_to_point(modify_point(control_point, size)) - point
        return point

    def set_font_type(self, font_face = None, font_slant = None, font_weight = None):
        if font_face is not None:
            self.font_face = font_face
        if font_slant is not None:
            self.font_slant = font_slant
        if font_weight is not None:
            self.font_weight = font_weight
        return self

    def match_font_type(self, text_obj):
        assert isinstance(text_obj, TextPartial)
        self.set_font_type(
            font_face = text_obj.font_face,
            font_slant = text_obj.font_slant,
            font_weight = text_obj.font_weight
        )
        return self


class Text(Mobject):
    CONFIG = {
        "aligned_direction": ORIGIN,
        "aligned_point_coord": ORIGIN,
        "font_size": 1.0,
        "font_face": "Sans",
        "font_slant": 0,
        "font_weight": 0,
        "buff_between_lines": 0.0,
    }

    def __init__(self, text, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.partial_text_list = text.split("\n")
        self.num_lines = len(self.partial_text_list)
        self.init_font_type()
        self.init_height()
        self.init_components()

    def font_to_height(self, font_sizes):
        return np.array([font_size * 1.0 for font_size in font_sizes])

    def init_font_type(self):
        self.font_type_attr_names = ("font_size", "font_face", "font_slant", "font_weight", \
            "stroke_width", "stroke_color", "fill_color")
        for attr_name in self.font_type_attr_names:
            attr_val = self.__dict__[attr_name]
            if isinstance(attr_val, tuple):
                assert len(attr_val) == self.num_lines
            else:
                self.__setattr__(attr_name, (attr_val,) * self.num_lines)
        return self

    def init_height(self):
        self.height = self.get_partial_height(self.num_lines) - self.buff_between_lines
        return self

    def get_partial_height(self, k):
        return (np.sum(self.font_to_height(self.font_size[:k])) + k * self.buff_between_lines)

    def get_control_point_and_direction(self):
        x, y = self.aligned_direction
        distance_to_top = ((1 - y) / 2) * self.height
        control_point = shift(self.aligned_point_coord, distance_to_top * UP)
        control_direction = np.array([x, 0])
        return (control_point, control_direction)

    def get_partial_text(self, k):
        control_point, control_direction = self.get_control_point_and_direction()
        font_kwargs = {}
        for attr_name in self.font_type_attr_names:
            font_kwargs[attr_name] = self.__getattribute__(attr_name)[k]
        partial_text = TextPartial(
            self.partial_text_list[k],
            aligned_direction = (control_direction + UP),
            aligned_point_coord = shift(control_point, self.get_partial_height(k) * DOWN),
            layer = self.layer,
            **font_kwargs
        )
        return partial_text

    def init_components(self):
        self.components = []
        for k in range(self.num_lines):
            partial_text = self.get_partial_text(k)
            self.components.append(partial_text)
        return self


