from maplib.constants import NAN

from maplib.tools.assertions import is_standard_route
from maplib.tools.assertions import station_on_route
from maplib.tools.config_ops import digest_locals
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.numpy_type_tools import np_to_tuple
from maplib.tools.position import position
from maplib.tools.simple_functions import adjacent_n_tuples
from maplib.tools.simple_functions import shrink_value
from maplib.tools.space_ops import midpoint
from maplib.tools.space_ops import num_to_base_direction
from maplib.tools.space_ops import restore_angle
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import solve_intersection_point
from maplib.utils.alignable import Frame


class Metro(object):
    """
    About input:
    serial_num: an int;
    metro_name: a str;
    main_color: a Color obj;
    sub_color: either a Color obj, None or "None";
    route_type: a str in ("l", "o", "y");
    stations_data: an array-like database, each of which should be of length 7 and be the following format:
        tuple(
            station_name_eng: a str,
            station_name_chn: a str,
            sign: either "*", "^" or "#" (
                if "*", the station_obj will not be built;
                if "^" or "#", a y-type route will be built
            ),
            station_x_coord: an int,
            station_y_coord: an int,
            simplified_direction: a positive integer in range(4),
            label_simple_direction: a positive integer in range(8)
        ).
    """
    def __init__(self, serial_num, metro_name, main_color, sub_color, route_type, stations_data):
        digest_locals(self)
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
        dict_value: tuple(
            sign,
            station_name_eng,
            station_name_chn,
            label_simple_direction
        )
        real_stations_data_dict
        dict_key: a tuple of a real station
        dict_value: tuple(
            station_color,
            sub_color,
            station_name_eng,
            station_name_chn,
            label_simple_direction
        )
        coord_to_direction_dict
        dict_key: a tuple of a point either given or calculated
        dict_value: simplified_direction
        """
        self.stations_data_dict = dict()
        self.real_stations_data_dict = dict()
        self.coord_to_direction_dict = dict()
        return self

    def digest_stations_data(self):
        self.loop = True if self.route_type == "o" else False
        self.station_coords = []
        self.signs = []
        for station_data in self.stations_data:
            station_name_eng, station_name_chn, sign, station_x_coord, station_y_coord, \
            simplified_direction, label_simple_direction = station_data
            station_coord = position(station_x_coord, station_y_coord)
            self.station_coords.append(station_coord)
            self.signs.append(sign)
            self.stations_data_dict[np_to_tuple(station_coord)] = (
                sign,
                station_name_eng,
                station_name_chn,
                label_simple_direction
            )
            self.coord_to_direction_dict[np_to_tuple(station_coord)] = simplified_direction
        return self

    def handle_non_y_type(self):
        coords = self.station_coords
        self.control_points = self.compute_control_points(coords)
        self.add_real_stations_data(self.control_points, coords)
        return self

    def handle_y_type(self):
        coords = self.station_coords
        branch_index = self.signs.index("^")
        follow_index = self.signs.index("#")
        main_coords = coords[:follow_index]
        sub_coords = coords[follow_index:]
        sub_coords.insert(0, coords[branch_index])
        self.main_control_points = self.compute_control_points(main_coords)
        self.sub_control_points = self.compute_control_points(sub_coords)
        self.add_real_stations_data(self.main_control_points, main_coords)
        self.add_real_stations_data(self.sub_control_points, sub_coords)
        return self

    def add_real_stations_data(self, control_points, station_coords):
        is_standard_route(control_points, self.loop)
        for station_coord in station_coords:
            station_data = self.stations_data_dict[np_to_tuple(station_coord)]
            if station_data[0] != "*":
                station_on_route(station_coord, control_points, self.loop)
                real_station_data = list(station_data)[1:]
                real_station_data = [self.main_color, self.sub_color] + real_station_data
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
        elif intersection_point is not NAN:
            control_points.append(intersection_point)
        return control_points

    def append_new_point(self, point1, point2, simplified_direction):
        rotated_point1, rotated_point2 = [
            rotate(np_float(point), -restore_angle(simplified_direction))
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


class Station(object):
    def __init__(self, center_point, route_colors, sub_colors, station_direction, \
            name_eng, name_chn, label_simple_direction):
        station_size = len(route_colors)
        label_direction = num_to_base_direction(label_simple_direction)
        digest_locals(self)

    def add_frame(self, station_frame):
        self.frame = Frame(station_frame.box_size)
        self.frame.align(self.center_point)
        return self


class DistrictNameModel(object):
    def __init__(self, name_eng, name_chn, x_coord, y_coord):
        center_point = position(x_coord, y_coord)
        digest_locals(self, ("name_eng", "name_chn", "center_point"))


class WaterAreaNameModel(object):
    def __init__(self, name_eng, name_chn, x_coord, y_coord):
        center_point = position(x_coord, y_coord)
        digest_locals(self, ("name_eng", "name_chn", "center_point"))

