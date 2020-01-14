import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Circle
from maplib.svg.svg_element import Mask
from maplib.svg.svg_element import Rectangle
from maplib.tools.assertions import assert_is_standard_route
from maplib.tools.assertions import assert_station_on_route
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.numpy_type_tools import np_to_tuple
from maplib.tools.simple_functions import adjacent_n_tuples
from maplib.tools.simple_functions import shrink_value
from maplib.tools.space_ops import get_positive_direction
from maplib.tools.space_ops import midpoint
from maplib.tools.space_ops import num_to_base_direction
from maplib.tools.space_ops import restore_angle
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import solve_intersection_point
from maplib.utils.alignable import Frame


class RouteMask(Mask):
    def __init__(self, metro_obj):
        id_name = metro_obj.mask_id_name
        Mask.__init__(self, id_name)
        self.use("mask_rect")
        self.use(metro_obj.route_id_name)


class NormalStationFrame(Circle):
    def __init__(self, metro_obj):
        id_name = metro_obj.frame_id_name
        radius = metro_obj.get_normal_station_frame_radius()
        Circle.__init__(self, id_name, radius)
        if params.STATION_FRAME_STYLE["stroke_color"]["normal"] is None:
            color = metro_obj.main_color
            self.set_style({
                "stroke": color,
            })


class InterchangeStationFrame(Rectangle):
    def __init__(self, station_obj):
        id_name = station_obj.frame_id_name
        radius = station_obj.get_interchange_station_frame_radius()
        box_size = station_obj.get_interchange_station_frame_box_size()
        Rectangle.__init__(self, id_name, box_size)
        self.align_at_origin()
        self.set_corner_radius(radius)


class StationPoint(Circle):
    def __init__(self, metro_obj):
        id_name = metro_obj.point_id_name
        color = metro_obj.main_color
        point_radius = params.STATION_POINT_STYLE["radius"]
        Circle.__init__(self, id_name, point_radius)
        self.set_style({
            "fill": color,
        })


class Metro(object):
    """
    About input:
    layer_num: an int;
    metro_name_dict: a tuple with different languages;
    main_color: a Color obj;
    sub_color: either a Color obj, None or "None";
    name_color: a Color obj;
    route_type: a str in ("l", "o", "y");
    names_coord: a list which contains coords of names of the metro;
    stations_data: an array-like database which contains 7 elements as the following format:
        station_x_coord: an int,
        station_y_coord: an int,
        simplified_direction: an integer in range(4),
        label_simple_direction: an integer in range(8),
        sign: either "*", "#" or "^" (
            if "*", the station_obj will not be built;
            if "#" or "^", a y-type route will be built
        ),
        station_name_eng: a str,
        station_name_chn: a str.
    """
    def __init__(self, layer_num, metro_name_dict, main_color, sub_color, name_color,
            route_type, names_coord, stations_data):
        self.layer_num = layer_num
        self.metro_name_dict = metro_name_dict
        self.main_color = main_color
        self.sub_color = sub_color
        self.name_color = name_color
        self.route_type = route_type
        self.names_coord = names_coord
        self.stations_data = stations_data
        layer_num_str = str(layer_num)
        self.route_id_name = "r" + layer_num_str
        self.mask_id_name = "m" + layer_num_str
        self.frame_id_name = "n" + layer_num_str
        self.point_id_name = "p" + layer_num_str
        self.sign_id_name = "s" + layer_num_str
        self.init_dicts()
        self.digest_stations_data()
        if self.route_type == "y":
            self.handle_y_type()
        else:
            self.handle_non_y_type()

    def init_dicts(self):
        """
        stations_data_dict
        dict_key: a tuple of a given point
        dict_val: tuple(
            sign,
            station_name_eng,
            station_name_chn,
            label_simple_direction
        )
        real_stations_data_dict
        dict_key: a tuple of a real station
        dict_val: tuple(
            metro,
            station_name_eng,
            station_name_chn,
            label_simple_direction
        )
        coord_to_direction_dict
        dict_key: a tuple of a point either given or calculated
        dict_val: simplified_direction
        """
        self.stations_data_dict = {}
        self.real_stations_data_dict = {}
        self.coord_to_direction_dict = {}
        return self

    def digest_stations_data(self):
        self.loop = True if self.route_type == "o" else False
        station_coords = []
        signs = []
        for station_data in self.stations_data:
            station_x_coord, station_y_coord, simplified_direction, label_simple_direction, \
                sign, station_name_eng, station_name_chn = station_data
            station_coord = np_float(station_x_coord, station_y_coord)
            station_coords.append(station_coord)
            signs.append(sign)
            self.stations_data_dict[np_to_tuple(station_coord)] = (
                sign,
                station_name_eng,
                station_name_chn,
                label_simple_direction
            )
            self.coord_to_direction_dict[np_to_tuple(station_coord)] = simplified_direction
        self.station_coords = station_coords
        self.signs = signs
        return self

    def handle_non_y_type(self):
        coords = self.station_coords
        self.control_points = self.compute_control_points(coords)
        self.add_real_stations_data(self.control_points, coords)
        return self

    def handle_y_type(self):
        coords = self.station_coords
        branch_index = self.signs.index("#")
        follow_index = self.signs.index("^")
        main_coords = coords[:follow_index]
        sub_coords = coords[follow_index:]
        sub_coords.insert(0, coords[branch_index])
        self.main_control_points = self.compute_control_points(main_coords)
        self.sub_control_points = self.compute_control_points(sub_coords)
        self.add_real_stations_data(self.main_control_points, main_coords)
        self.add_real_stations_data(self.sub_control_points, sub_coords)
        return self

    def add_real_stations_data(self, control_points, station_coords):
        assert_is_standard_route(control_points, self.loop)
        for station_coord in station_coords:
            station_data = self.stations_data_dict[np_to_tuple(station_coord)]
            if station_data[0] != "*":
                assert_station_on_route(station_coord, control_points, self.loop)
                real_station_data = list(station_data)[1:]
                real_station_data.insert(0, self)
                self.real_stations_data_dict[np_to_tuple(station_coord)] = tuple(real_station_data)
        return self

    def compute_control_points(self, station_coords):
        control_points = []
        for point1, point2 in adjacent_n_tuples(station_coords, 2, self.loop):
            control_points = self.update_control_point(point1, point2, control_points)
        if not self.loop:
            control_points.insert(0, station_coords[0])
            control_points.append(station_coords[-1])
        return control_points

    def update_control_point(self, point1, point2, control_points):
        simplified_direction1 = self.coord_to_direction_dict[np_to_tuple(point1)]
        simplified_direction2 = self.coord_to_direction_dict[np_to_tuple(point2)]
        theta1, theta2 = [
            restore_angle(simplified_direction)
            for simplified_direction in [simplified_direction1, simplified_direction2]
        ]
        intersection_point = solve_intersection_point(point1, theta1, point2, theta2)
        if intersection_point is None:
            simplified_direction = simplified_direction1
            append_point = self.append_new_point(point1, point2, simplified_direction)
            control_points = self.update_control_point(point1, append_point, control_points)
            control_points = self.update_control_point(point2, append_point, control_points)
        elif intersection_point is not consts.NAN:
            control_points.append(intersection_point)
        return control_points

    def append_new_point(self, point1, point2, simplified_direction):
        rotated_point1, rotated_point2 = [
            rotate(point, -restore_angle(simplified_direction))
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
        self.coord_to_direction_dict[np_to_tuple(append_point)] = append_direction
        return append_point

    def get_name_dict(self):
        eng_name = self.metro_name_dict[consts.ENG]
        if eng_name.startswith("Line "):
            return {
                consts.ENG: eng_name.split()[1],
            }
        return self.metro_name_dict

    def get_name_type(self):
        name_dict = self.get_name_dict()
        return "number" if len(name_dict) == 1 else "strings"

    def get_route(self):
        id_name = self.route_id_name
        arc_radius = params.ROUTE_STYLE["arc_radius"]
        if self.route_type == "l":
            return LPath(id_name, self.control_points, arc_radius)
        if self.route_type == "o":
            return OPath(id_name, self.control_points, arc_radius)
        if self.route_type == "y":
            return YPath(id_name, self.main_control_points, self.sub_control_points, arc_radius)
        raise NotImplementedError(self.route_type)

    def get_mask(self):
        return RouteMask(self)

    def set_mask(self, mask_template):
        self.mask = mask_template
        return self

    def get_normal_station_frame_radius(self):
        return params.STATION_FRAME_STYLE["radius"]["normal"]

    def get_normal_station_frame(self):
        return NormalStationFrame(self)

    def get_station_point(self):
        return StationPoint(self)


class Station(object):
    def __init__(self, center_point, parent_metros, station_direction,
            station_name_dict, label_simple_direction):
        self.center_point = center_point
        self.parent_metros = parent_metros
        self.station_direction = station_direction
        self.station_name_dict = station_name_dict
        station_size = len(parent_metros)
        self.station_size = station_size
        self.label_direction = num_to_base_direction(label_simple_direction)
        if station_size == 1:
            self.init_normal_station()
        else:
            self.init_interchange_station()

    def get_name_dict(self):
        return self.station_name_dict

    def init_normal_station(self):
        self.is_normal = True
        self.parent_metro = self.parent_metros[0]
        self.set_normal_station_frame()
        return self

    def init_interchange_station(self):
        self.is_normal = False
        self.frame_id_name = self.station_direction + str(self.station_size)
        self.station_type = (self.station_size, self.station_direction)
        positive_direction = get_positive_direction(self.station_direction)
        positioned_point = self.center_point - (self.station_size - 1) * positive_direction / 2
        self.point_coords = [(positioned_point + k * positive_direction) for k in range(self.station_size)]
        self.set_interchange_station_frame()

    def get_interchange_station_frame_radius(self):
        return params.STATION_FRAME_STYLE["radius"]["interchange"]

    def get_interchange_station_frame_box_size(self):
        radius = self.get_interchange_station_frame_radius()
        x = self.station_size - 1 + 2 * radius
        y = 2 * radius
        if self.station_direction == consts.VERTICAL:
            x, y = y, x
        return np_float(x, y)

    def get_interchange_station_frame(self):
        return InterchangeStationFrame(self)

    def set_frame(self, box_size):
        frame = Frame(box_size)
        frame.align(self.center_point)
        self.frame = frame
        return self

    def set_normal_station_frame(self):
        radius = self.parent_metro.get_normal_station_frame_radius()
        box_size = 2 * radius * consts.RU
        self.set_frame(box_size)
        return self

    def set_interchange_station_frame(self):
        box_size = self.get_interchange_station_frame_box_size()
        self.set_frame(box_size)
        return self


class SimpleName(object):
    def __init__(self, x_coord, y_coord, name_eng, name_chn):
        self.name_dict = {
            consts.ENG: name_eng,
            consts.CHN: name_chn,
        }
        self.center_point = np_float(x_coord, y_coord)

    def get_name_dict(self):
        return self.name_dict


class MetroName(object):
    def __init__(self, metro_obj, coord):
        self.metro_obj = metro_obj
        self.center_point = coord
        self.color = metro_obj.name_color

    def get_name_dict(self):
        return self.metro_obj.get_name_dict()
