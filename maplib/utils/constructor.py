import copy

from maplib.constants import *

from maplib.tools.simple_functions import get_first_item
from maplib.tools.simple_functions import string_to_nums
from maplib.tools.space_ops import center_of_mass
from maplib.tools.table_tools import get_row_val
from maplib.tools.table_tools import get_table_val
from maplib.tools.table_tools import open_xlsx_file
from maplib.utils.color import Color
from maplib.utils.models import DistrictNameModel
from maplib.utils.models import Metro
from maplib.utils.models import Station
from maplib.utils.models import WaterAreaNameModel


class Constructor(object):
    def __init__(self, file_name):
        self.database = open_xlsx_file(file_name)
        self.build_metros()
        self.build_stations()
        self.build_district_names()
        self.build_water_area_names()

    def build_metros(self):
        self.metros = []
        self.all_stations_data_dict = dict()
        main_sheet = self.database["main"]
        num_metros = main_sheet.max_row
        for k in range(num_metros):
            metro_basic_data = get_row_val(main_sheet, row_index = k, max_column = 6)
            metro_name, metro_name_chn, metro_serial_num, \
                main_color_str, sub_color_str, route_type = metro_basic_data
            main_color = Color(*string_to_nums(main_color_str))
            if sub_color_str is not None and sub_color_str != "None":
                sub_color = Color(*string_to_nums(sub_color_str))
            else:
                sub_color = sub_color_str
            metro_stations_data = get_table_val(self.database[metro_name], max_column = 7)
            metro = Metro(
                metro_serial_num,
                metro_name,
                main_color,
                sub_color,
                route_type,
                metro_stations_data
            )
            self.metros.append(metro)
            self.all_stations_data_dict.update(metro.real_stations_data_dict)
        self.metros.sort(key = lambda metro: metro.serial_num)
        return self

    def build_stations(self):
        self.station_coord_tuples = list(self.all_stations_data_dict.keys())
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
        center_point = center_of_mass(adjacent_coord_list)
        station_data = [self.all_stations_data_dict[coord] for coord in adjacent_coord_list]
        colors, sub_colors, station_names_eng, station_names_chn, label_simple_directions = zip(*station_data)
        station = Station(
            center_point,
            colors,
            sub_colors,
            station_direction,
            get_first_item(station_names_eng),
            get_first_item(station_names_chn),
            get_first_item(label_simple_directions)
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
                    extended_coord_tuple = tuple(coord + direction)
                    if extended_coord_tuple in self.station_coord_tuples:
                        new_adjacent_coord_set.add(extended_coord_tuple)
        return new_adjacent_coord_set

    def build_obj(self, obj_name, table_name, max_column, ModelClass):
        obj_list = []
        sheet = self.database[table_name]
        data = get_table_val(sheet, max_column = max_column)
        for district_name_data in data:
            obj = ModelClass(*district_name_data)
            obj_list.append(obj)
        self.__setattr__(obj_name, obj_list)
        return self

    def build_district_names(self):
        self.build_obj("district_names", "district name", 4, DistrictNameModel)
        return self

    def build_water_area_names(self):
        self.build_obj("water_area_names", "water area name", 4, WaterAreaNameModel)
        return self

