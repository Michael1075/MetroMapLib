from maplib.constants import *
from maplib.parameters import *

from maplib.svg.path_types import LineArcPath
from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Circle
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Rectangle
from maplib.tools.config_ops import digest_locals
from maplib.tools.position import position
from maplib.tools.space_ops import get_positive_direction


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


class WebSystem(Group):
    def __init__(self, id_name, metro_objs, station_objs):
        digest_locals(self, ("metro_objs", "station_objs"))
        Group.__init__(self, id_name)
        self.init_dicts()
        self.classify_stations()
        self.add_route()
        self.add_normal_station_frame()
        self.add_interchange_station_frame()
        self.add_station_frame()
        self.add_station_point()

    def init_dicts(self):
        self.serial_num_to_color_dict = dict()
        self.color_to_serial_num_dict = dict()
        for metro in self.metro_objs:
            self.serial_num_to_color_dict[metro.serial_num] = metro.color
            self.color_to_serial_num_dict[metro.color.hex_str()] = metro.serial_num
        self.id_to_frame_dict = dict()
        return self

    def classify_stations(self):
        self.normal_stations = []
        self.interchange_stations = []
        for station in self.station_objs:
            if station.station_size == 1:
                self.normal_stations.append(station)
            else:
                self.interchange_stations.append(station)
        return self

    def add_route(self):
        routes_group = Group("route")
        routes_group.set_style({
            "fill": None,
            "stroke-opacity": ROUTE_STROKE_OPACITY,
            "stroke-width": ROUTE_STROKE_WIDTH,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        for metro in self.metro_objs[::-1]:
            route_obj = Route(metro)
            routes_group.append(route_obj)
        self.append(routes_group)
        return self

    def add_normal_station_frame(self):
        for serial_num, color in self.serial_num_to_color_dict.items():
            station_id_name = "n" + str(serial_num)
            template = NormalStationFrame(station_id_name, color)
            self.id_to_frame_dict[station_id_name] = template
            self.append(template)
        normal_station_frame_group = Group("normal_station_frame")
        normal_station_frame_group.set_style({
            "stroke-width": FRAME_STROKE_WIDTH_DICT["normal"],
        })
        for station in self.normal_stations:
            color = station.route_colors[0]
            serial_num = self.color_to_serial_num_dict[color.hex_str()]
            station_id_name = "n" + str(serial_num)
            station.add_frame(self.id_to_frame_dict[station_id_name])
            normal_station_frame_group.use(station_id_name, station.positioned_point)
        self.append(normal_station_frame_group)
        return self

    def add_interchange_station_frame(self):
        station_type_set = set()
        for station in self.interchange_stations:
            station_type_set.add((station.station_direction, station.station_size))
        for direction, size in list(station_type_set):
            station_id_name = direction + str(size)
            template = InterchangeStationFrame(station_id_name, size, direction)
            self.id_to_frame_dict[station_id_name] = template
            self.append(template)
        interchange_station_frame_group = Group("interchange_station_frame")
        interchange_station_frame_group.set_style({
            "stroke": INTERCHANGE_STATION_FRAME_STROKE_COLOR,
            "stroke-width": FRAME_STROKE_WIDTH_DICT["interchange"],
        })
        for station in self.interchange_stations:
            station_id_name = station.station_direction + str(station.station_size)
            station.add_frame(self.id_to_frame_dict[station_id_name])
            interchange_station_frame_group.use(station_id_name, station.positioned_point)
        self.append(interchange_station_frame_group)
        return self

    def add_station_frame(self):
        station_frame_group = Group("station_frame")
        station_frame_group.set_style({
            "fill": FRAME_FILL_COLOR,
            "stroke-opacity": FRAME_STROKE_OPACITY,
        })
        station_frame_group.use("normal_station_frame")
        station_frame_group.use("interchange_station_frame")
        self.append(station_frame_group)
        return self

    def add_station_point(self):
        for serial_num, color in self.serial_num_to_color_dict.items():
            template = StationPoint("p" + str(serial_num), color)
            self.append(template)
        station_point_group = Group("station_point")
        station_point_group.set_style({
            "fill-opacity": STATION_POINT_FILL_OPACITY,
        })
        for station in self.interchange_stations:
            for k, color in enumerate(station.route_colors):
                serial_num = self.color_to_serial_num_dict[color.hex_str()]
                positive_direction = get_positive_direction(station.station_direction)
                positioned_point = station.positioned_point + k * positive_direction
                station_point_group.use("p" + str(serial_num), positioned_point)
        self.append(station_point_group)
        return self

