from maplib.constants import *
from maplib.parameters import *

from maplib.svg.path_types import LineArcPath
from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Circle
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Mask
from maplib.svg.svg_element import Rectangle
from maplib.tools.config_ops import digest_locals
from maplib.tools.position import position
from maplib.tools.space_ops import get_positive_direction


class FrameRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name)
        self.set_rect_size(SIZE)
        self.set_style({
            "stroke-width": 0,
        })


class Route(LineArcPath):
    def __init__(self, id_name, metro):
        arc_radius = ROUTE_ARC_RADIUS
        if metro.route_type == "l":
            LPath.__init__(self, id_name, metro.control_points, arc_radius)
        elif metro.route_type == "o":
            OPath.__init__(self, id_name, metro.control_points, arc_radius)
        elif metro.route_type == "y":
            YPath.__init__(self, id_name, metro.main_control_points, metro.sub_control_points, arc_radius)
        else:
            raise TypeError


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
        self.init_template_group()
        self.init_dicts()
        self.classify_stations()
        self.def_frame_rect()
        self.add_route()
        self.add_normal_station_frame()
        self.add_interchange_station_frame()
        self.add_station_frame()
        self.add_station_point()

    def init_template_group(self):
        self.template_group = Group("template")
        return self

    def init_dicts(self):
        self.serial_num_to_color_dict = dict()
        self.color_to_serial_num_dict = dict()
        for metro in self.metro_objs:
            self.serial_num_to_color_dict[metro.serial_num] = metro.main_color
            self.color_to_serial_num_dict[metro.main_color.hex_str()] = metro.serial_num
        self.id_to_mask_dict = dict()
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

    def def_frame_rect(self):
        frame_rect_obj = FrameRectangle("frame_rect")
        frame_rect_obj.set_style({
            "fill": WHITE,
        })
        self.template_group.append(frame_rect_obj)

    def add_route(self):
        route_mask_group = Group("route_mask")
        route_mask_group.set_style({
            "fill": None,
            "stroke-width": ROUTE_MINOR_STROKE_WIDTH,
            "stroke": BLACK,
        })
        for metro in self.metro_objs:
            route_path_id_name = "r" + str(metro.serial_num)
            route_path_template = Route(route_path_id_name, metro)
            self.template_group.append(route_path_template)
            if metro.sub_color is not None:
                mask_id_name = "m" + str(metro.serial_num)
                mask = Mask(mask_id_name)
                mask.use("frame_rect")
                mask.use(route_path_id_name)
                self.id_to_mask_dict[route_path_id_name] = mask
                route_mask_group.append(mask)
        self.template_group.append(route_mask_group)

        route_group = Group("route")
        route_group.set_style({
            "fill": None,
            "stroke-opacity": ROUTE_STROKE_OPACITY,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        for metro in self.metro_objs[::-1]:
            route_path_id_name = "r" + str(metro.serial_num)
            if metro.sub_color is None:
                route_group.use_with_style(route_path_id_name, {
                    "stroke-width": ROUTE_STROKE_WIDTH,
                    "stroke": metro.main_color,
                })
            else:
                mask = self.id_to_mask_dict[route_path_id_name]
                route_group.use_with_style(route_path_id_name, {
                    "stroke-width": ROUTE_STROKE_WIDTH,
                    "stroke": metro.main_color,
                    "mask": mask,
                })
                if metro.sub_color != "None":
                    route_group.use_with_style(route_path_id_name, {
                        "stroke-width": ROUTE_MINOR_STROKE_WIDTH,
                        "stroke": metro.sub_color,
                    })
        self.append(route_group)
        return self

    def add_normal_station_frame(self):
        for serial_num, color in self.serial_num_to_color_dict.items():
            station_id_name = "n" + str(serial_num)
            template = NormalStationFrame(station_id_name, color)
            self.id_to_frame_dict[station_id_name] = template
            self.template_group.append(template)

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
            self.template_group.append(template)

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
            point_id_name = "p" + str(serial_num)
            template = StationPoint(point_id_name, color)
            self.template_group.append(template)
            
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
