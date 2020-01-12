import maplib.constants as consts
import maplib.parameters as params

from maplib.tools.simple_functions import get_first_item
from maplib.tools.simple_functions import modify_num
from maplib.tools.simple_functions import string_to_nums
from maplib.tools.space_ops import center_of_mass
from maplib.utils.color import Color
from maplib.utils.models import Metro
from maplib.utils.models import SimpleNameModel
from maplib.utils.models import Station


class Constructor(object):
    def __init__(self):
        self.input_dict = params.INPUT_DATABASE_DICT
        self.all_stations_data_dict = {}
        self.metro_objs = self.build_metros()
        self.station_coord_tuples = list(self.all_stations_data_dict.keys())
        self.station_objs = self.build_stations()
        self.name_objs_dict = self.build_name_objs()
        self.geography_data_dict = self.build_geography_objs()

    @staticmethod
    def string_to_vals(string, num_vals=None, merge_index=None, modify_indexes=None):
        if num_vals is None:
            components = string.split()
        else:
            if merge_index is None:
                merge_index = num_vals - 1
            components = string.split(maxsplit=merge_index)
            right_part = components.pop()
            rmaxsplit = num_vals - merge_index - 1
            components.extend(right_part.rsplit(maxsplit=rmaxsplit))
        if modify_indexes is None:
            modify_indexes = ()
        result = []
        for k, s in enumerate(components):
            if s == "-":
                val = None
            else:
                try:
                    val = float(s)
                    if k in modify_indexes:
                        val = modify_num(val)
                except ValueError:
                    val = s
            result.append(val)
        return result

    @staticmethod
    def format_list_with_strs(data, flush_left_indexes=None):
        if flush_left_indexes is None:
            flush_left_indexes = ()
        result_lists = []
        for single_data in data:
            strs = []
            for val in single_data:
                if val is None:
                    s = "-"
                else:
                    try:
                        val = modify_num(val)
                    except ValueError:
                        pass
                    s = str(val)
                strs.append(s)
            result_lists.append(strs)
        zipped_lists = list(zip(*result_lists))
        max_lengths = [
            max([len(s) for s in zipped_lists[k]])
            for k in range(len(zipped_lists))
        ]
        result = []
        for strs in result_lists:
            single_list = []
            for k, s in enumerate(strs):
                spaces = " " * (max_lengths[k] - len(s))
                if k in flush_left_indexes:
                    s += spaces
                else:
                    s = spaces + s
                single_list.append(s)
            single_str = " ".join(single_list).rstrip()
            result.append(single_str)
        return result

    @staticmethod
    def get_metro_data(metro_dict):
        metro_name_dict = metro_dict["name"]
        serial_num = metro_dict["serial_num"]
        color_str = metro_dict["color"]
        main_color = Color(*string_to_nums(color_str))
        sub_color_str = metro_dict["sub_color"]
        if sub_color_str is not None and sub_color_str != "None":
            sub_color = Color(*string_to_nums(sub_color_str))
        else:
            sub_color = sub_color_str
        route_type = metro_dict["route_type"]
        stations_data = []
        for station_data_str in metro_dict["stations_data"]:
            station_data = Constructor.string_to_vals(station_data_str, 7, 5, (2, 3))
            stations_data.append(station_data)
        return serial_num, metro_name_dict, main_color, sub_color, route_type, stations_data

    @staticmethod
    def format_metro_dict(serial_num, metro_name_dict, main_color, sub_color, route_type, stations_data):
        color_str = main_color.simple_str()
        if sub_color is not None and sub_color != "None":
            sub_color_str = sub_color.simple_str()
        else:
            sub_color_str = sub_color
        stations_data_strs = Constructor.format_list_with_strs(stations_data, (5, 6))
        return {
            "name": metro_name_dict,
            "serial_num": serial_num,
            "color": color_str,
            "sub_color": sub_color_str,
            "route_type": route_type,
            "stations_data": stations_data_strs,
        }

    def build_metros(self):
        metro_objs = []
        for metro_dict in self.input_dict["metro_database"]:
            metro_data = Constructor.get_metro_data(metro_dict)
            metro = Metro(*metro_data)
            metro_objs.append(metro)
            self.all_stations_data_dict.update(metro.real_stations_data_dict)
        metro_objs.sort(key = lambda metro: metro.serial_num)
        return metro_objs

    def build_stations(self):
        station_objs = []
        while self.station_coord_tuples:
            station_obj = self.build_station()
            station_objs.append(station_obj)
        return station_objs

    def build_station(self):
        station_coord_tuple = self.station_coord_tuples[0]
        adjacent_coord_list = list(self.expand_station(station_coord_tuple))
        adjacent_coord_list.sort(key = lambda coord: sum(coord))
        for adjacent_coord in adjacent_coord_list:
            self.station_coord_tuples.remove(adjacent_coord)
        x, y = zip(*adjacent_coord_list)
        if max(y) == min(y):
            station_direction = consts.HORIZONTAL
        elif max(x) == min(x):
            station_direction = consts.VERTICAL
        else:
            raise ValueError(adjacent_coord_list)
        center_point = center_of_mass(adjacent_coord_list)
        station_data = [self.all_stations_data_dict[coord] for coord in adjacent_coord_list]
        parent_metros, station_names_eng, station_names_chn, label_simple_directions = zip(*station_data)
        station_name_dict = {
            consts.ENG: get_first_item(station_names_eng),
            consts.CHN: get_first_item(station_names_chn),
        }
        label_simple_direction = get_first_item(label_simple_directions)
        station = Station(
            center_point,
            parent_metros,
            station_direction,
            station_name_dict,
            label_simple_direction
        )
        return station

    def expand_station(self, station_coord_tuple):
        old_adjacent_coord_set = set()
        new_adjacent_coord_set = {station_coord_tuple}
        while len(new_adjacent_coord_set - old_adjacent_coord_set) != 0:
            old_adjacent_coord_set = new_adjacent_coord_set.copy()
            for coord in list(old_adjacent_coord_set):
                for direction in consts.FOUR_BASE_DIRECTIONS:
                    extended_coord_tuple = tuple(coord + direction)
                    if extended_coord_tuple in self.station_coord_tuples:
                        new_adjacent_coord_set.add(extended_coord_tuple)
        return new_adjacent_coord_set

    @staticmethod
    def get_name_data(name_data_str):
        x_coord, y_coord, name_eng, name_chn = Constructor.string_to_vals(name_data_str, 4, 2)
        return x_coord, y_coord, name_eng, name_chn

    @staticmethod
    def get_name_type_data(name_data_strs):
        return [Constructor.get_name_data(name_data_str) for name_data_str in name_data_strs]

    @staticmethod
    def format_name_type_list(name_data):
        return Constructor.format_list_with_strs(name_data, (2, 3))

    def build_name_objs(self):
        name_objs_dict = {}
        for name_type, name_data_strs in self.input_dict["name_database"].items():
            name_obj_list = []
            for name_data_str in name_data_strs:
                name_data = Constructor.get_name_data(name_data_str)
                name_obj = SimpleNameModel(*name_data)
                name_obj_list.append(name_obj)
            name_objs_dict[name_type] = name_obj_list
        return name_objs_dict

    @staticmethod
    def get_geography_data(obj_dict):
        coord_data_strs = obj_dict.pop("coord_data")
        obj_data = []
        for coord_data_str in coord_data_strs:
            coord_data = Constructor.string_to_vals(coord_data_str)
            obj_data.append(coord_data)
        return obj_dict, obj_data

    @staticmethod
    def format_geography_obj_dict(obj_dict, obj_data):
        obj_dict["coord_data"] = Constructor.format_list_with_strs(obj_data)
        return obj_dict

    def build_geography_objs(self):
        geography_data_dict = {}
        for obj_type, objs in self.input_dict["geography_database"].items():
            geography_data_dict[obj_type] = []
            for obj_dict in objs:
                geography_data = Constructor.get_geography_data(obj_dict)
                geography_data_dict[obj_type].append(geography_data)
        return geography_data_dict
