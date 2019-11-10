from openpyxl import load_workbook
import copy

from maplib.constants import *
from maplib.parameters import *

from maplib.tools.assertions import is_standard_route
from maplib.tools.assertions import station_on_route
from maplib.tools.config_ops import digest_locals
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.numpy_type_tools import np_to_tuple
from maplib.tools.position import position
from maplib.tools.simple_functions import adjacent_n_tuples
from maplib.tools.simple_functions import get_first_item
from maplib.tools.simple_functions import shrink_value
from maplib.tools.space_ops import midpoint
from maplib.tools.space_ops import num_to_base_direction
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import solve_intersection_point
from maplib.utils.color import Color


class Metro(object):
    """
    About input:
    serial_num: an int;
    metro_name: a str;
    color: a Color obj;
    route_type: a str in ("l", "o", "y");
    stations_data: an array-like database, each of which should be of length 7 and be the following format:
        tuple(
            station_name_eng: a str,
            station_name_chn: a str,
            station_x_coord: an int,
            station_y_coord: an int,
            simplified_direction: a positive integer in range(4),
            label_direction_num: a positive integer in range(8),
            sign: either "*", "^" or "#" (
                if "*", the station_obj will not be built;
                if "^" or "#", then a y-type routewill be built
            )
        ).
    """
    def __init__(self, serial_num, metro_name, color, route_type, stations_data):
        digest_locals(self)
        self.init_dicts()
        self.digest_stations_data()
        if self.route_type == "y":
            self.handle_y_type()
        else:
            self.handle_non_y_type()

    def init_dicts(self):
        """
        station_data_dict
        dict_key: a tuple of a given point
        dict_value: tuple(
            sign,
            station_name_eng,
            station_name_chn,
            label_direction
        )
        real_station_data_dict
        dict_key: a tuple of a real station
        dict_value: tuple(
            station_color,
            station_name_eng,
            station_name_chn,
            label_direction
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
            simplified_direction, label_direction_num = station_data
            station_coord = position(station_x_coord, station_y_coord)
            self.station_coords.append(station_coord)
            self.signs.append(sign)
            self.stations_data_dict[np_to_tuple(station_coord)] = (
                sign,
                station_name_eng,
                station_name_chn,
                num_to_base_direction(label_direction_num)
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
                real_station_data.insert(0, self.color)
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
            simplified_direction * PI / 4
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
        # Some extra user-defined points and particular arc_radius should also be added,
        # but not this function itself
        rotated_point1, rotated_point2 = [
            rotate(np_float(point), -simplified_direction * PI / 4)
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
    def __init__(self, positioned_point, route_colors, station_direction, station_name_eng, station_name_chn, label_direction):
        station_size = len(route_colors)
        digest_locals(self)

    def add_frame(self, station_frame):
        self.station_frame = station_frame
        self.aligned_point = self.get_critical_point(self.label_direction)
        self.aligned_direction = -self.label_direction
        return self

    def get_critical_point(self, direction):
        return self.positioned_point + self.station_frame.get_critical_vector(direction)


class MetroBuilder(object):
    def __init__(self, file_name):
        self.metros = []
        self.all_stations_data_dict = dict()
        self.digest_data_and_build(file_name)

    def digest_data_and_build(self, file_name):
        database = load_workbook(filename = file_name)
        main_sheet = database["Main"]
        for k in range(1, len(database.worksheets)):
            metro_basic_data = tuple([
                cell.value
                for cell in main_sheet["A{0}:G{0}".format(k)][0]
            ])
            metro_name, metro_name_chn, metro_serial_num, \
                red, green, blue, route_type = metro_basic_data
            metro_color = Color(red, green, blue)
            #if special_control_point is not None:
            #    special_control_point = eval(special_control_point)
            #if special_arc_radius is not None:
            #    special_arc_radius = eval(special_arc_radius)
            metro_stations_data_table = database[metro_name]
            metro_stations_data = tuple([
                tuple([
                    row[row_index].value
                    for row_index in range(7)
                ])
                for row in metro_stations_data_table
            ])
            metro = Metro(
                metro_serial_num,
                metro_name,
                metro_color,
                route_type,
                metro_stations_data,
                #special_control_point = special_control_point,
                #special_arc_radius = special_arc_radius
            )
            self.metros.append(metro)
            self.all_stations_data_dict.update(metro.real_stations_data_dict)
        return self


class StationBuilder(object):
    def __init__(self, station_data_dict):
        self.station_data_dict = station_data_dict
        self.station_coord_tuples = list(station_data_dict.keys())
        self.stations = []
        while self.station_coord_tuples:
            self.build_station()

    def build_station(self):
        station_coord_tuple = self.station_coord_tuples[0]
        adjacent_coord_list = list(self.expand_station(station_coord_tuple))
        adjacent_coord_list.sort(key = lambda coord: sum(coord))
        for adjacent_coord in adjacent_coord_list:
            self.station_coord_tuples.remove(adjacent_coord)
        x, y = zip(*adjacent_coord_list)
        if max(y) == min(y):
            station_direction = HORIZONTAL
        elif max(x) == min(x):
            station_direction = VERTICAL
        else:
            raise AssertionError
        positioned_point = position(min(x), min(y))
        station_data = [self.station_data_dict[coord] for coord in adjacent_coord_list]
        colors, station_names_eng, station_names_chn, label_directions = zip(*station_data)
        station_name_eng = get_first_item(station_names_eng)
        station_name_chn = get_first_item(station_names_chn)
        label_direction = get_first_item(label_directions)
        station = Station(
            positioned_point,
            colors,
            station_direction,
            station_name_eng,
            station_name_chn,
            label_direction
        )
        self.stations.append(station)
        return self

    def expand_station(self, station_coord_tuple):
        old_adjacent_coord_set = set()
        new_adjacent_coord_set = {station_coord_tuple}
        while len(new_adjacent_coord_set - old_adjacent_coord_set) != 0:
            old_adjacent_coord_set = copy.copy(new_adjacent_coord_set)
            for coord in list(old_adjacent_coord_set):
                for direction in FOUR_BASE_DIRECTIONS:
                    extended_coord_tuple = tuple([
                        (c + d)
                        for c, d in zip(coord, direction)
                    ])
                    if extended_coord_tuple in self.station_coord_tuples:
                        new_adjacent_coord_set.add(extended_coord_tuple)
        return new_adjacent_coord_set

