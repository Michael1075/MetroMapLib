from openpyxl import load_workbook
import copy
import numpy as np

from attributes import global_station_data_dict

from constants import *

from mobject.composite_mobject import Metro
from mobject.composite_mobject import Station

from tools.numpy_type_tools import int64

from tools.simple_functions import get_color_rgb
from tools.simple_functions import get_first_item


class DataLoader(object):
    def __init__(self):
        self.metros = []
        self.digest_data_and_build()

    def digest_data_and_build(self):
        database = load_workbook(filename = "files\\input_file\\data.xlsx")
        main_sheet = database["Main"]
        for k in range(1, len(database.worksheets)):
            metro_basic_data = tuple([
                cell.value
                for cell in main_sheet["A{0}:K{0}".format(k)][0]
            ])
            metro_name, metro_name_chn, metro_serial_num, metro_color_hex, red, green, blue, \
                metro_color_name, loop, special_control_point, special_arc_radius = metro_basic_data
            metro_color_rgb = tuple([primary_color / 255 for primary_color in (red, green, blue)])
            if metro_color_name is not None:
                metro_color_name = eval(metro_color_name)
            if special_control_point is not None:
                special_control_point = eval(special_control_point)
            if special_arc_radius is not None:
                special_arc_radius = eval(special_arc_radius)
            metro_stations_data_table = database[metro_name]
            metro_stations_data = tuple([(
                (row[2].value, row[3].value),
                row[4].value,
                row[5].value,
                row[0].value,
                row[1].value
            ) for row in metro_stations_data_table])
            metro = Metro(
                metro_serial_num,
                get_color_rgb(metro_color_name),
                metro_stations_data,
                loop = loop,
                special_control_point = special_control_point,
                special_arc_radius = special_arc_radius
            )
            self.metros.append(metro)
        return self


class StationBuilder(object):
    def __init__(self, station_data_dict):
        self.station_data_dict = station_data_dict
        self.station_coord_tuples = list(station_data_dict.keys())
        self.stations = []
        while len(self.station_coord_tuples) != 0:
            self.build_station()

    def build_station(self):
        station_coord_tuple = self.station_coord_tuples[0]
        adjacent_coord_list = list(self.expand_station(station_coord_tuple))
        adjacent_coord_list.sort(key = lambda coord: sum(coord))
        for adjacent_coord in adjacent_coord_list:
            self.station_coord_tuples.remove(adjacent_coord)
        x, y = zip(*adjacent_coord_list)
        if max(y) == min(y):
            station_direction = "h"
        elif max(x) == min(x):
            station_direction = "v"
        center_point = np.average(np.array(adjacent_coord_list), axis = 0)
        station_data = [self.station_data_dict[coord] for coord in adjacent_coord_list]
        colors, station_names, station_names_chn, label_directions = zip(*station_data)
        station_name = get_first_item(station_names)
        station_name_chn = get_first_item(station_names_chn)
        label_direction = get_first_item(label_directions)
        station = Station(
            center_point,
            colors,
            station_direction = station_direction,
            station_name = station_name,
            station_name_chn = station_name_chn,
            label_direction = label_direction
        )
        self.stations.append(station)
        return self

    def expand_station(self, station_coord_tuple):
        old_adjacent_coord_set = set()
        new_adjacent_coord_set = {station_coord_tuple}
        while len(new_adjacent_coord_set - old_adjacent_coord_set) != 0:
            old_adjacent_coord_set = copy.copy(new_adjacent_coord_set)
            for coord in list(old_adjacent_coord_set):
                for direction in (RIGHT, LEFT, UP, DOWN):
                    extended_coord_tuple = tuple(int64(np.array(coord) + direction))
                    if extended_coord_tuple in self.station_coord_tuples:
                        new_adjacent_coord_set.update({extended_coord_tuple})
        return new_adjacent_coord_set


loader = DataLoader()
metro_objs = loader.metros
builder = StationBuilder(global_station_data_dict)
station_objs = builder.stations

