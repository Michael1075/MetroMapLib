import numpy as np

from constants import *
from parameters import *

from svg.svg_element import Circle
from svg.svg_element import Path
from svg.svg_element import Rectangle
from tools.assertions import is_standard_route
from tools.config_ops import digest_locals
from tools.position import position
from tools.simple_functions import adjacent_n_tuples
from tools.space_ops import abs_arg_pair
from tools.space_ops import arg
from tools.space_ops import get_angle
from tools.space_ops import get_positive_direction
from tools.space_ops import rotate
from tools.space_ops import unify_vector


class LineArcPath(Path):
    def __init__(self, id_name, control_points, arc_radius, loop):
        digest_locals(self)
        is_standard_route(control_points, loop)
        Path.__init__(self, id_name)
        self.num_arcs = len(control_points)
        if not self.loop:
            self.num_arcs -= 2
        self.create_path()

    def create_path(self):
        before_arc_points = []
        after_arc_points = []
        sweep_flags = []
        for a, b, c in adjacent_n_tuples(self.control_points, 3, self.loop):
            theta = get_angle(a, b, c)
            sweep_flag = 0 if theta >= 0.0 else 1
            cut_off_length = self.arc_radius / np.tan(abs(theta) / 2)
            h1, h2 = [
                (b + abs_arg_pair(cut_off_length, arg(p - b)))
                for p in [a, c]
            ]
            before_arc_points.append(h1)
            after_arc_points.append(h2)
            sweep_flags.append(sweep_flag)
        if not self.loop:
            before_arc_points.append(self.control_points[-1])
            after_arc_points.append(self.control_points[0])

        self.move_to(after_arc_points[-1])
        for k in range(self.num_arcs):
            self.line_to(before_arc_points[k])
            self.arc_to(after_arc_points[k], self.arc_radius, 0, sweep_flags[k])
        if self.loop:
            self.close_path()
        else:
            self.line_to(before_arc_points[-1])
        self.finish_path()
        return self


class LPath(LineArcPath):
    def __init__(self, id_name, control_points, arc_radius):
        LineArcPath.__init__(self, id_name, control_points, arc_radius, False)


class OPath(LineArcPath):
    def __init__(self, id_name, control_points, arc_radius):
        LineArcPath.__init__(self, id_name, control_points, arc_radius, True)


class YPath(LineArcPath):
    def __init__(self, id_name, main_control_points, sub_control_points, arc_radius):
        LineArcPath.__init__(self, id_name, main_control_points, arc_radius, False)
        sub_path = LineArcPath(None, sub_control_points, arc_radius, False)
        self.add_element_path(sub_path)


class Route(LineArcPath):
    def __init__(self, metro):
        id_name = metro.metro_name.replace(" ", "_")
        arc_radius = ROUTE_ARC_RADIUS
        if metro.route_type == "l":
            LPath.__init__(self, id_name, metro.control_points, arc_radius)
        elif metro.route_type == "o":
            OPath.__init__(self, id_name, metro.control_points, arc_radius)
        elif metro.route_type == "y":
            YPath.__init__(self, id_name, metro.main_control_points, metro.sub_control_points, arc_radius)
        else:
            raise TypeError
        self.set_style({"stroke": metro.color})


class NormalStationFrame(Circle):
    def __init__(self, id_name, color):
        radius = FRAME_RADIUS_DICT["normal"]
        digest_locals(self)
        Circle.__init__(self, id_name)
        self.set_radius(radius)
        self.set_style({
            "stroke": color,
        })

    def get_critical_vector(self, direction):
        return RU * self.radius * direction


class InterchangeStationFrame(Rectangle):
    def __init__(self, id_name, station_size, station_direction):
        radius = FRAME_RADIUS_DICT["interchange"]
        digest_locals(self)
        x = station_size - 1 + 2 * radius
        y = 2 * radius
        if station_direction == VERTICAL:
            x, y = y, x
        self.station_rect_size = position(x, y)
        relative_coord = LD * radius
        Rectangle.__init__(self, id_name)
        self.set_rect_size(self.station_rect_size)
        self.set_rect_relative_coord(relative_coord)
        self.set_corner_radius(radius)

    def get_critical_vector(self, direction):
        positive_direction = get_positive_direction(self.station_direction)
        positioned_point_to_center = (self.station_size - 1) * positive_direction / 2
        return positioned_point_to_center + self.station_rect_size / 2 * direction


class StationPoint(Circle):
    def __init__(self, id_name, color):
        point_radius = STATION_POINT_RADIUS
        Circle.__init__(self, id_name)
        self.set_radius(point_radius)
        self.set_style({
            "fill": color,
        })


class BackgroundRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name)
        self.set_rect_size(SIZE)
        self.set_style({
            "fill": WATER_AREA_COLOR,
        })


class Land(LPath):
    def __init__(self, id_name, control_points, add_corners = None):
        arc_radius = COASTLINE_ARC_RADIUS
        LPath.__init__(self, id_name, control_points, arc_radius)
        if add_corners is not None:
            for corner in add_corners:
                corner_coord = (corner + RU) * SIZE / 2
                self.line_to(corner_coord)
        self.close_path()
        self.finish_path()


class Island(OPath):
    def __init__(self, id_name, control_points):
        arc_radius = COASTLINE_ARC_RADIUS
        OPath.__init__(self, id_name, control_points, arc_radius)


class River(YPath):
    def __init__(self, id_name, control_points):
        arc_radius = RIVER_ARC_RADIUS_DICT[id_name]
        river_width = RIVER_WIDTH_DICT[id_name]
        digest_locals(self)
        main_control_points, sub_control_points = self.compute_river_control_points()
        YPath.__init__(self, id_name, main_control_points, sub_control_points, arc_radius)
        self.set_style({
            "stroke-width": river_width,
        })

    def compute_river_control_points(self):
        last_given_point = self.control_points[-1]
        unit_vector = unify_vector(last_given_point - self.control_points[-2])
        middle_point = last_given_point + self.river_width * unit_vector / 2
        former_point = middle_point - self.arc_radius * unit_vector
        last_right_point = rotate(former_point, PI / 2, middle_point)
        last_left_point = rotate(former_point, -PI / 2, middle_point)
        main_control_points = self.control_points[:-1]
        main_control_points.extend([middle_point, last_right_point])
        sub_control_points = [former_point, middle_point, last_left_point]
        return main_control_points, sub_control_points


class Lake(Circle):
    def __init__(self, id_name, radius, center_coord):
        Circle.__init__(self, id_name)
        self.set_radius(radius)
        self.set_circle_center_coord(center_coord)

