import maplib.constants as consts

from maplib.tools.sheet_tools import get_workbook_data_dict
from maplib.tools.simple_functions import get_first_item
from maplib.tools.simple_functions import string_to_nums
from maplib.tools.space_ops import center_of_mass
from maplib.utils.color import Color
from maplib.utils.models import Metro
from maplib.utils.models import SimpleNameModel
from maplib.utils.models import Station


class Constructor(object):
    def __init__(self, metro_file_name, geography_file_name):
        self.metro_database_dict = get_workbook_data_dict(metro_file_name, child_sheet_max_column = 7)
        self.geography_database_dict = get_workbook_data_dict(geography_file_name, ignore_none = True)
        self.build_metros()
        self.build_stations()
        self.build_name_obj()
        self.build_geometry_data()

    def build_metros(self):
        self.metro_objs = []
        self.all_stations_data_dict = dict()
        for metro_name, metro_data in self.metro_database_dict.items():
            metro_basic_data, metro_stations_data = metro_data
            metro_name_chn, metro_serial_num, main_color_str, sub_color_str, route_type = metro_basic_data
            main_color = Color(*string_to_nums(main_color_str))
            if sub_color_str is not None and sub_color_str != "None":
                sub_color = Color(*string_to_nums(sub_color_str))
            else:
                sub_color = sub_color_str
            metro = Metro(
                metro_serial_num,
                metro_name,
                main_color,
                sub_color,
                route_type,
                metro_stations_data
            )
            self.metro_objs.append(metro)
            self.all_stations_data_dict.update(metro.real_stations_data_dict)
        self.metro_objs.sort(key = lambda metro: metro.serial_num)
        return self

    def build_stations(self):
        self.station_coord_tuples = list(self.all_stations_data_dict.keys())
        self.station_objs = []
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
            station_direction = consts.HORIZONTAL
        elif max(x) == min(x):
            station_direction = consts.VERTICAL
        else:
            raise ValueError(adjacent_coord_list)
        center_point = center_of_mass(adjacent_coord_list)
        station_data = [self.all_stations_data_dict[coord] for coord in adjacent_coord_list]
        parent_metros, station_names_eng, station_names_chn, label_simple_directions = zip(*station_data)
        station = Station(
            center_point,
            parent_metros,
            station_direction,
            get_first_item(station_names_eng),
            get_first_item(station_names_chn),
            get_first_item(label_simple_directions)
        )
        self.station_objs.append(station)
        return self

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

    def build_name_obj(self):
        self.name_objs_dict = dict()
        for name_type, data in self.geography_database_dict.items():
            name_type = name_type.replace(" ", "_")
            basic_data, detailed_data = data
            if basic_data[0] == "name":
                obj_list = []
                for component_data in detailed_data:
                    obj = SimpleNameModel(*component_data)
                    obj_list.append(obj)
                self.name_objs_dict[name_type] = obj_list
        return self

    def build_geometry_data(self):
        geometry_obj_types = ("Land", "Island", "River", "Lake", "InnerLake")
        self.geometry_data_dict = {obj_type: [] for obj_type in geometry_obj_types}
        for obj_name, data in self.geography_database_dict.items():
            basic_data, detailed_data = data
            obj_type = basic_data[0]
            if obj_type in geometry_obj_types:
                rest_basic_data = [float(val) for val in basic_data[1:]]
                rest_basic_data.insert(0, obj_name)
                self.geometry_data_dict[obj_type].append((rest_basic_data, detailed_data))
        return self

