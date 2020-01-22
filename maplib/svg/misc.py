from xml.dom import minidom

import maplib.constants as consts

from maplib.svg.svg_element import Group
from maplib.svg.svg_element import LinearGradient
from maplib.svg.svg_element import Mask
from maplib.svg.svg_element import Path
from maplib.svg.svg_element import Rectangle
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.space_ops import shrink_value
from maplib.tools.space_ops import is_horizontal
from maplib.tools.space_ops import get_simplified_direction
from maplib.utils.alignable import Frame
from maplib.utils.alignable import SvgFrame
from maplib.utils.params_getter import Container


class BackgroundFrame(Frame):
    def __init__(self):
        Container.__init__(self)
        Frame.__init__(self, self.params.BODY_SIZE)
        self.align_at_origin(consts.LD)


class BodyRectangle(Rectangle):
    def __init__(self, id_name):
        Container.__init__(self)
        Rectangle.__init__(self, id_name, self.params.BODY_SIZE)
        self.set_style({
            "stroke-width": 0.,
        })


class FullRectangle(Rectangle):
    def __init__(self, id_name):
        Container.__init__(self)
        Rectangle.__init__(self, id_name, self.params.FULL_SIZE)
        self.set_style({
            "stroke-width": 0.,
        })


class BodyMaskRectangle(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.use_with_style("body_rect", {
            "fill": self.params.MASK_BASE_COLOR,
        })


class MaskRectangle(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.use_with_style("full_rect", {
            "fill": self.params.MASK_BASE_COLOR,
        })


class SidePart(Rectangle):
    def __init__(self, id_name):
        Container.__init__(self)
        Rectangle.__init__(self, id_name, self.params.FULL_SIZE)
        mask = self.get_mask()
        self.template = mask
        self.set_style({
            "stroke-width": 0.,
            "fill": self.params.MAIN_COLOR,
            "mask": mask,
        })

    def get_mask(self):
        mask = Mask("metro_map_mask")
        mask.use_with_style("full_rect", {
            "fill": self.params.MASK_BASE_COLOR,
        })
        mask.use_with_style("body_rect", {
            "fill": self.params.MASK_COLOR,
        }, self.params.MAP_GROUP_SHIFT_VECTOR)
        return mask


class Grid(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        grid_style = self.params.GRID_STYLE
        if grid_style["has_grid"]:
            self.set_style({
                "stroke": grid_style["color"],
                "stroke-opacity": grid_style["stroke_opacity"],
                "stroke-width": grid_style["stroke_width"],
            })
            path = self.get_path(grid_style["step"])
            self.append(path)

    def get_path(self, step):
        body_width = self.params.BODY_WIDTH
        body_height = self.params.BODY_HEIGHT
        path = Path(None)
        for k in range(*[round(val) for val in (step, body_width, step)]):
            path.move_to(np_float(k, 0))
            path.line_to(np_float(k, body_height))
        for k in range(*[round(val) for val in (step, body_height, step)]):
            path.move_to(np_float(0, k))
            path.line_to(np_float(body_width, k))
        path.finish_path()
        return path


class GradientFrame(Group):
    def __init__(self, gradient_color):
        self.gradient_color = gradient_color
        Group.__init__(self, None)
        for direction in consts.FOUR_BASE_DIRECTIONS:
            gradient_obj = self.get_gradient_obj(direction)
            self.append(gradient_obj)

    def get_gradient_obj(self, direction):
        direction_num = shrink_value(get_simplified_direction(direction) // 2, 0, 4)
        gradient_id_name = "grad" + str(direction_num)
        gradient_obj = LinearGradient(gradient_id_name, direction)
        gradient_obj.add_begin_color(self.gradient_color, 0.)
        gradient_obj.add_end_color(self.gradient_color, 1.)
        return gradient_obj


class MapFrame(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        background_frame = BackgroundFrame()
        gradient_frame = GradientFrame(self.params.MAIN_COLOR)
        self.template = gradient_frame
        for direction in consts.FOUR_BASE_DIRECTIONS:
            if is_horizontal(direction):
                rect_box_size = np_float(self.params.GRADIENT_WIDTH, self.params.BODY_HEIGHT)
            else:
                rect_box_size = np_float(self.params.BODY_WIDTH, self.params.GRADIENT_HEIGHT)
            side_rectangle = Rectangle(None, rect_box_size)
            side_rectangle.align(background_frame.get_critical_point(direction), direction)
            side_rectangle.set_style({
                "fill": gradient_frame.get_gradient_obj(direction)
            })
            self.append(side_rectangle)


class NumberNameFrame(Rectangle):
    def __init__(self, metro_obj):
        Container.__init__(self)
        id_name = metro_obj.sign_id_name
        radius = self.params.SIGN_NAME_STYLE["corner_radius"]
        box_size = self.params.SIGN_NAME_STYLE["number_frame_side_length"] * consts.RU
        Rectangle.__init__(self, id_name, box_size)
        self.align_at_origin()
        self.set_corner_radius(radius)
        self.set_style({
            "fill": metro_obj.main_color,
        })


class StringsNameFrame(Rectangle):
    def __init__(self, metro_obj, tex_box_size):
        Container.__init__(self)
        id_name = metro_obj.sign_id_name
        radius = self.params.SIGN_NAME_STYLE["corner_radius"]
        box_size = tex_box_size + self.params.SIGN_NAME_STYLE["strings_frame_side_buff"] * consts.RU
        Rectangle.__init__(self, id_name, box_size)
        self.align_at_origin()
        self.set_corner_radius(radius)
        self.set_style({
            "fill": metro_obj.main_color,
        })


class SvgPathTemplate(Group, Frame):
    def __init__(self, id_name, svg_dir, scale_factor, color):
        Group.__init__(self, id_name)
        doc = minidom.parse(svg_dir)
        original_box_size = SvgFrame(svg_dir).box_size
        paths = doc.getElementsByTagName("path")
        box_size = original_box_size * scale_factor
        Frame.__init__(self, box_size)
        self.scale_and_shift(scale_factor, -box_size / 2)
        self.set_style({
            "fill": color,
        })
        for path in paths:
            path_cmd = path.getAttribute("d")
            path_obj = Path(None)
            path_obj.add_raw_command(path_cmd)
            path_obj.finish_path()
            self.append(path_obj)
        doc.unlink()
