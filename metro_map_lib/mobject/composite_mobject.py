from attributes import *

from constants import *

from mobject.mobject import ArcBetweenPoints
from mobject.mobject import Circle
from mobject.mobject import Mobject
from mobject.mobject import Line
from mobject.mobject import Text

from tools.assertions import is_2D_data
from tools.assertions import is_standard_route
from tools.assertions import station_on_route

from tools.config_ops import digest_locals

from tools.numpy_type_tools import float64
from tools.numpy_type_tools import int64

from tools.simple_functions import adjacent_n_tuples
from tools.simple_functions import modify_point
from tools.simple_functions import shrink_value
from tools.simple_functions import unit_to_point

from tools.space_ops import abs_arg_pair
from tools.space_ops import arg_C
from tools.space_ops import arg_principle
from tools.space_ops import get_angle
from tools.space_ops import get_base_direction
from tools.space_ops import get_critical_point_about_center_vector
from tools.space_ops import get_positive_direction
from tools.space_ops import judge_direction
from tools.space_ops import midpoint
from tools.space_ops import num_to_base_direction
from tools.space_ops import rotate
from tools.space_ops import shift
from tools.space_ops import solve_intersection_point


class LineArcCurve(Mobject):
    CONFIG = {
        "loop": False,
        "arc_radius": ARC_RADIUS,
    }

    def __init__(self, *control_points, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        assert is_2D_data(*control_points)
        self.num_arcs = len(control_points)
        if not self.loop:
            self.num_arcs -= 2

    def get_real_points_and_angles(self):
        points = self.control_points
        radius = self.arc_radius
        loop = self.loop
        before_arc_points = []
        after_arc_points = []
        angles = []
        for a, b, c in adjacent_n_tuples(points, 3, loop):
            theta = get_angle(a, b, c)
            cut_off_length = radius / np.tan(abs(theta) / 2)
            h1, h2 = [
                shift(b, abs_arg_pair(cut_off_length, arg_C(p - b)))
                for p in [a, c]
            ]
            angle = arg_principle(theta + PI)
            before_arc_points.append(h1)
            after_arc_points.append(h2)
            angles.append(angle)
        if not loop:
            before_arc_points.append(points[-1])
            after_arc_points.append(points[0])
        return (before_arc_points, after_arc_points, angles)


    def generate(self, ctx, size):
        before_arc_points, after_arc_points, angles = self.get_real_points_and_angles()
        ctx.move_to(*unit_to_point(modify_point(after_arc_points[-1], size)))
        for k in range(self.num_arcs):
            arc = ArcBetweenPoints(
                before_arc_points[k],
                after_arc_points[k],
                angle = angles[k],
                stroke_width = self.stroke_width,
                stroke_color = self.stroke_color
            )
            ctx.line_to(*unit_to_point(modify_point(before_arc_points[k], size)))
            ctx = arc.generate(ctx, size)
        if not self.loop:
            ctx.line_to(*unit_to_point(modify_point(before_arc_points[-1], size)))
        return ctx


class Route(Mobject):
    CONFIG = {
        "loop": False,
        "arc_radius": ARC_RADIUS,
        "stroke_width": ROUTE_STROKE_WIDTH,
        "stroke_opacity": ROUTE_STROKE_OPACITY,
    }

    def __init__(self, *control_points, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.init_components()

    def init_components(self):
        route = LineArcCurve(
            *self.control_points,
            loop = self.loop,
            arc_radius = self.arc_radius,
            layer = self.layer,
            stroke_width = self.stroke_width,
            stroke_color = self.stroke_color,
            stroke_opacity = self.stroke_opacity,
            fill_color = self.fill_color
        )
        self.components = [route]
        return self


class RouteLoop(Route):
    CONFIG = {
        "loop": True,
    }


class StationFrame(Mobject):
    CONFIG = {
        "layer": 1,
        "station_direction": "h",
        "frame_radius_dict": FRAME_RADIUS_DICT,
        "frame_stroke_width_dict": FRAME_STROKE_WIDTH_DICT,
        "fill_color": FRAME_FILL_COLOR,
    }

    def __init__(self, center_point, station_size, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.station_type = "normal" if self.station_size == 1 else "interchange"
        self.frame_radius = self.get_frame_radius()
        self.frame_stroke_width = self.get_frame_stroke_width()
        self.init_box_size()
        control_points = self.get_frame_control_points()
        station_frame = RouteLoop(
            *control_points,
            arc_radius = self.frame_radius,
            stroke_width = self.frame_stroke_width,
            fill_color = self.fill_color,
            layer = self.layer,
            **kwargs
        )
        self.components = [station_frame]

    def get_frame_radius(self):
        return self.frame_radius_dict[self.station_type]

    def get_frame_stroke_width(self):
        return self.frame_stroke_width_dict[self.station_type]

    def init_box_size(self):
        radius = self.frame_radius
        x, y = self.station_size, 1
        if self.station_direction == "v":
            x, y = y, x
        self.box_size = np.array([x, y])
        return self

    def get_frame_control_points(self):
        radius = self.frame_radius
        x, y = (self.station_size - 1) / 2 + radius, radius
        if self.station_direction == "v":
            x, y = y, x
        cx, cy = self.center_point
        control_points = np.array([
            [cx + x, cy + y],
            [cx - x, cy + y],
            [cx - x, cy - y],
            [cx + x, cy - y],
        ])
        return control_points


class StationPoint(Circle):
    CONFIG = {
        "layer": 2,
        "radius": STATION_POINT_RADIUS,
        "stroke_width": 0.0,
        "fill_opacity": STATION_POINT_FILL_OPACITY,
    }

    def __init__(self, center_point, **kwargs):
        Circle.__init__(
            self,
            arc_center = center_point,
            **kwargs
        )


class Station(Mobject):
    CONFIG = {
        "station_direction": "h",
        "has_label": HAS_LABEL,
        "chn_up": CHN_UP,
        "station_name": None,
        "station_name_chn": None,
        "label_direction": None,
        "label_layer": 3,
        "label_buff": STATION_LABEL_BUFF,
        "label_font_size": LABEL_FONT_SIZE,
        "label_font_face": LABEL_FONT_FACE,
        "label_font_face_chn": LABEL_FONT_FACE_CHN,
        "label_stroke_width": LABEL_STROKE_WIDTH,
        "label_stroke_color": LABEL_STROKE_COLOR,
        "label_text_color": LABEL_TEXT_COLOR,
    }

    def __init__(self, center_point, route_colors, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.station_size = len(route_colors)
        self.init_components()

    def init_components(self):
        self.init_geometry_components()
        if self.has_label and all(attr is not None for attr in [
            self.station_name,
            self.station_name_chn,
            self.label_direction
        ]):
            self.init_label()
        return self

    def init_geometry_components(self):
        center_point = self.center_point
        station_size = self.station_size
        direction = self.station_direction
        self.components = []
        if self.station_size == 1:
            frame = StationFrame(
                center_point,
                station_size,
                station_direction = direction,
                stroke_color = self.route_colors[0]
            )
            self.frame = frame
            self.components.append(frame)
        else:
            frame = StationFrame(
                center_point,
                station_size,
                station_direction = direction
            )
            self.frame = frame
            self.components.append(frame)
            positive_direction = get_positive_direction(direction)
            first_point = point = center_point - (station_size - 1) / 2 * positive_direction
            for k in range(station_size):
                point = first_point + k * positive_direction
                station_point = StationPoint(
                    point,
                    fill_color = self.route_colors[k]
                )
                self.components.append(station_point)
        return self

    def init_label(self):
        up_str = self.station_name_chn
        down_str = self.station_name
        font_face = (self.label_font_face_chn, self.label_font_face)
        if not self.chn_up:
            up_str, down_str = down_str, up_str
            font_face = font_face[::-1]
        name_str = up_str + "\n" + down_str
        label = Text(
            name_str,
            layer = self.label_layer,
            aligned_direction = -self.label_direction,
            aligned_point_coord = self.get_aligned_point(),
            font_size = self.label_font_size,
            font_face = font_face,
            stroke_width = self.label_stroke_width,
            stroke_color = self.label_stroke_color,
            fill_color = self.label_text_color
        )
        self.components.append(label)
        return self

    def get_critical_point(self, direction):
        return shift(
            self.center_point,
            get_critical_point_about_center_vector(direction, self.frame.box_size)
        )

    def get_aligned_point(self):
        return shift(
            self.get_critical_point(self.label_direction),
            self.label_direction * self.label_buff
        )


class Metro(Mobject):
    """
    About input:
    serial_num: an int;
    color: in HEX(a str headed by "#") or rgb(a 3-element tuple);
    stations_data: an array-like database, each of which should be of length 2 or 4 and be the following format:
        tuple(
            station_coord: a 2-element tuple,
            simplified_direction: a positive integer in range(4)[,
            label_direction_num: a positive integer in range(8),
            station_name: a str (if "*", the station_obj will not be built),
            station_name_chn: a str]
        ).
    Optionals:
    loop: a boolean;
    #special_control_point: TODO
    """
    CONFIG = {
        "loop": False,
        #"special_control_point": None,
        #"special_arc_radius": None,
    }

    def __init__(self, serial_num, color, stations_data, **kwargs):
        global global_station_data_dict
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.digest_stations_data()
        self.init_control_points()
        self.init_components()

    def digest_stations_data(self):
        self.station_coords = np.zeros((0, 2))
        self.coord_to_direction_dict = {}
        self.label_directions = []
        self.station_names = []
        self.station_names_chn = []
        for station_data in self.stations_data:
            station_coord_tuple, simplified_direction, label_direction_num, station_name, station_name_chn = station_data
            station_coord = float64(np.array(station_coord_tuple))
            self.station_coords = np.r_[self.station_coords, [station_coord]]
            self.coord_to_direction_dict[tuple(station_coord)] = simplified_direction
            self.label_directions.append(num_to_base_direction(label_direction_num))
            self.station_names.append(station_name)
            self.station_names_chn.append(station_name_chn)
        return self

    def init_control_points(self):
        self.control_points = np.zeros((0, 2))
        for point1, point2 in adjacent_n_tuples(self.station_coords, 2, self.loop):
            self.compute_control_point(point1, point2)
        if not self.loop:
            self.control_points = np.r_[[self.station_coords[0]], self.control_points]
            self.control_points = np.r_[self.control_points, [self.station_coords[-1]]]
        return self

    def compute_control_point(self, point1, point2):
        simplified_direction1 = self.coord_to_direction_dict[tuple(point1)]
        simplified_direction2 = self.coord_to_direction_dict[tuple(point2)]
        theta1, theta2 = [
            simplified_direction * PI / 4
            for simplified_direction in [simplified_direction1, simplified_direction2]
        ]
        intersection_point = solve_intersection_point(point1, theta1, point2, theta2)
        if intersection_point is None:
            simplified_direction = simplified_direction1
            append_point = self.append_new_point(point1, point2, simplified_direction)
            self.compute_control_point(point1, append_point)
            self.compute_control_point(point2, append_point)
        elif intersection_point is np.nan:
            return self
        else:
            self.control_points = np.r_[self.control_points, [intersection_point]]
        return self

    def append_new_point(self, point1, point2, simplified_direction):
        # some extra user-defined points and particular arc_radius should also be added,
        # but not this function itself
        rotated_point1, rotated_point2 = [
            rotate(point, -simplified_direction * PI / 4)
            for point in [point1, point2]
        ]
        distance_vec = rotated_point2 - rotated_point1
        h, v = distance_vec[0], distance_vec[1]
        if v < 0:
            h, v = -h, -v
        if h > v:
            append_direction = 1
        elif h < -v:
            append_direction = 3
        else:
            append_direction = 2
        append_point = midpoint(point1, point2)
        append_direction = shrink_value(simplified_direction + append_direction, 0, 4)
        self.coord_to_direction_dict[tuple(append_point)] = append_direction
        return append_point

    def init_components(self):
        self.components = []
        self.config_route()
        for k in range(len(self.station_coords)):
            if self.station_names[k] != "*":
                self.add_station_data(k)
        return self

    def config_route(self):
        layer_num = -self.serial_num
        loop = self.loop
        control_points = self.control_points
        assert is_standard_route(control_points, loop)
        route = Route(
            *control_points,
            loop = loop,
            layer = layer_num,
            stroke_color = self.color
        )
        self.components.append(route)
        return self

    def add_station_data(self, k):
        station_coord = self.station_coords[k]
        assert station_on_route(station_coord, self.control_points, self.loop)
        new_station_data = (
            self.color,
            self.station_names[k],
            self.station_names_chn[k],
            self.label_directions[k]
        )
        global_station_data_dict[tuple(int64(station_coord))] = new_station_data
        return self


class MetroLoop(Metro):
    CONFIG = {
        "loop": True,
    }

