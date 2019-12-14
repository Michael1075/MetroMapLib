from xml.dom import minidom

import maplib.constants as consts
import maplib.parameters as params

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


class BackgroundFrame(Frame):
    def __init__(self):
        Frame.__init__(self, params.FRAME_SIZE)
        self.align_at_origin(consts.LD)


class FrameRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name, params.FRAME_SIZE)
        self.set_style({
            "stroke-width": 0.,
        })


class FullRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name, params.FULL_SIZE)
        self.set_style({
            "stroke-width": 0.,
        })


class SidePart(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name, params.FULL_SIZE)
        mask = self.get_mask()
        self.mask = mask
        self.set_style({
            "stroke-width": 0.,
            "fill": params.MAIN_COLOR,
            "mask": mask,
        })

    def get_mask(self):
        mask = Mask("metro_map_mask")
        mask.use_with_style("full_rect", {
            "fill": params.MASK_BASE_COLOR,
        })
        mask.use_with_style("frame_rect", {
            "fill": params.MASK_COLOR,
        }, params.MAIN_FRAME_SHIFT_VECTOR)
        return mask


class Grid(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.set_style({
            "stroke": params.GRID_COLOR,
            "stroke-opacity": params.GRID_STROKE_OPACITY,
            "stroke-width": params.ROUTE_STROKE_WIDTH,
        })
        path = self.get_path()
        self.append(path)

    def get_path(self):
        path = Path(None)
        for k in range(*[round(val) for val in (
            params.GRID_STEP, params.FRAME_WIDTH, params.GRID_STEP
        )]):
            path.move_to(np_float(k, 0))
            path.line_to(np_float(k, params.FRAME_HEIGHT))
        for k in range(*[round(val) for val in (
            params.GRID_STEP, params.FRAME_HEIGHT, params.GRID_STEP
        )]):
            path.move_to(np_float(0, k))
            path.line_to(np_float(params.FRAME_WIDTH, k))
        path.finish_path()
        return path


class GradientFrame(Group):
    def get_gradient_obj(self, direction):
        direction_num = shrink_value(get_simplified_direction(direction) // 2, 0, 4)
        gradient_id_name = "grad" + str(direction_num)
        gradient_obj = LinearGradient(gradient_id_name, direction)
        gradient_obj.add_begin_color(params.GRADIENT_MASK_COLOR, 0.)
        gradient_obj.add_end_color(params.GRADIENT_MASK_COLOR, 1.)
        return gradient_obj

    def append_components(self):
        for direction in consts.FOUR_BASE_DIRECTIONS:
            gradient_obj = self.get_gradient_obj(direction)
            self.append(gradient_obj)
        return self


class MapFrame(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        background_frame = BackgroundFrame()
        gradient_frame = GradientFrame(None)
        for direction in consts.FOUR_BASE_DIRECTIONS:
            if is_horizontal(direction):
                rect_box_size = np_float(params.GRADIENT_WIDTH, params.FRAME_HEIGHT)
            else:
                rect_box_size = np_float(params.FRAME_WIDTH, params.GRADIENT_HEIGHT)
            side_rectangle = Rectangle(None, rect_box_size)
            side_rectangle.align(background_frame.get_critical_point(direction), direction)
            side_rectangle.set_style({
                "fill": gradient_frame.get_gradient_obj(direction)
            })
            self.append(side_rectangle)


class SvgPathObject(Group, Frame):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        doc = minidom.parse(self.svg_info["svg_dir"])
        original_box_size = np_float(*[
            doc.getElementsByTagName("svg")[0].getAttribute(attr_name)
            for attr_name in ("width", "height")
        ])
        path_cmd = doc.getElementsByTagName("path")[0].getAttribute("d")
        doc.unlink()
        scale_factor = self.svg_info["scale_factor"]
        box_size = original_box_size * scale_factor
        Frame.__init__(self, box_size)
        self.align(self.svg_info["aligned_point"])
        shift_vector = self.get_critical_point(consts.LD)
        self.scale_and_shift(scale_factor, shift_vector)
        path = Path(None)
        path.add_raw_command(path_cmd)
        path.finish_path()
        self.append(path)
        self.set_style({
            "fill": self.svg_info["color"],
        })


class ShanghaiMetroLogo(SvgPathObject):
    svg_info = params.METRO_LOGO_INFO

