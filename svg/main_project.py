from constants import *
from parameters import *

from svg.canva import Canva
from svg.geography import GeograpicMap
from svg.svg_composite import InterchangeStationFrame
from svg.svg_composite import NormalStationFrame
from svg.svg_composite import Route
from svg.svg_composite import StationPoint
from svg.svg_element import Group
from svg.svg_element import Path#
from svg.svg_element import Use#
from svg.tex import Tex
from svg.tex import TexBox
from tools.color import Color#
from tools.constructor import MetroBuilder
from tools.constructor import StationBuilder
from tools.position import position#
from tools.simple_functions import close_to
from tools.space_ops import get_positive_direction
from tools.space_ops import get_simplified_direction


class Project(Canva):
    def construct(self):
        self.load_data()
        self.init_dicts_and_sets()
        self.classify_stations()
        self.def_geographic_map()
        self.def_web()#
        self.def_route()
        self.def_normal_station_frame()
        self.def_interchange_station_frame()
        self.def_station_frame()
        self.def_station_point()
        self.def_station_name()
        self.def_station_name_shadow()
        self.create_project()

    def load_data(self):
        metro_builder = MetroBuilder()
        station_data_dict = metro_builder.all_stations_data_dict
        station_builder = StationBuilder(station_data_dict)
        self.metro_objs = metro_builder.metros
        self.metro_objs.sort(key = lambda obj: obj.serial_num)
        self.station_objs = station_builder.stations

    def init_dicts_and_sets(self):
        self.serial_num_to_color_dict = dict()
        self.color_to_serial_num_dict = dict()
        for metro in self.metro_objs:
            self.serial_num_to_color_dict[metro.serial_num] = metro.color
            self.color_to_serial_num_dict[metro.color.hex_str()] = metro.serial_num
        self.id_to_frame_dict = dict()
        self.tex_path_id_set = set()

    def classify_stations(self):
        self.normal_stations = []
        self.interchange_stations = []
        for station in self.station_objs:
            if station.station_size == 1:
                self.normal_stations.append(station)
            else:
                self.interchange_stations.append(station)

    def def_geographic_map(self):
        geographic_map = GeograpicMap()
        self.define(geographic_map)

    def def_web(self):#
        hpath = Path("h")
        hpath.move_to(position(0, 0)).h_line_to(WIDTH).finish_path()
        vpath = Path("v")
        vpath.move_to(position(0, 0)).v_line_to(HEIGHT).finish_path()
        group1 = Group("group1").set_style({
            "stroke": Color(180, 180, 180),
            "stroke-opacity": 0.6,
            "stroke-width": 2,
        })
        self.define(hpath)
        self.define(vpath)
        self.define(group1)

        for i in range(0, 400, 50):
            group1.use("v", position(i, 0))
        for i in range(0, 300, 50):
            group1.use("h", position(0, i))

    def def_route(self):
        routes_group = Group("route").set_style({
            "fill": None,
            "stroke-opacity": ROUTE_STROKE_OPACITY,
            "stroke-width": ROUTE_STROKE_WIDTH,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        for metro in self.metro_objs[::-1]:
            route_obj = Route(metro)
            routes_group.append(route_obj)
        self.define(routes_group)

    def def_normal_station_frame(self):
        for serial_num, color in self.serial_num_to_color_dict.items():
            station_id_name = "n" + str(serial_num)
            template = NormalStationFrame(station_id_name, color)
            self.id_to_frame_dict[station_id_name] = template
            self.define(template)
        normal_station_frame_group = Group("normal_station_frame").set_style({
            "stroke-width": FRAME_STROKE_WIDTH_DICT["normal"],
        })
        for station in self.normal_stations:
            color = station.route_colors[0]
            serial_num = self.color_to_serial_num_dict[color.hex_str()]
            station_id_name = "n" + str(serial_num)
            station.add_frame(self.id_to_frame_dict[station_id_name])
            normal_station_frame_group.use(station_id_name, station.positioned_point)
        self.define(normal_station_frame_group)

    def def_interchange_station_frame(self):
        station_type_set = set()
        for station in self.interchange_stations:
            station_type_set.add((station.station_direction, station.station_size))
        for direction, size in list(station_type_set):
            station_id_name = direction + str(size)
            template = InterchangeStationFrame(station_id_name, size, direction)
            self.id_to_frame_dict[station_id_name] = template
            self.define(template)
        interchange_station_frame_group = Group("interchange_station_frame").set_style({
            "stroke": INTERCHANGE_STATION_FRAME_STROKE_COLOR,
            "stroke-width": FRAME_STROKE_WIDTH_DICT["interchange"],
        })
        for station in self.interchange_stations:
            station_id_name = station.station_direction + str(station.station_size)
            station.add_frame(self.id_to_frame_dict[station_id_name])
            interchange_station_frame_group.use(station_id_name, station.positioned_point)
        self.define(interchange_station_frame_group)

    def def_station_frame(self):
        station_frame_group = Group("station_frame").set_style({
            "fill": FRAME_FILL_COLOR,
            "stroke-opacity": FRAME_STROKE_OPACITY,
        })
        station_frame_group.use("normal_station_frame")
        station_frame_group.use("interchange_station_frame")
        self.define(station_frame_group)

    def def_station_point(self):
        for serial_num, color in self.serial_num_to_color_dict.items():
            template = StationPoint("p" + str(serial_num), color)
            self.define(template)
        station_point_group = Group("station_point").set_style({
            "fill-opacity": STATION_POINT_FILL_OPACITY,
        })
        for station in self.interchange_stations:
            for k, color in enumerate(station.route_colors):
                serial_num = self.color_to_serial_num_dict[color.hex_str()]
                positive_direction = get_positive_direction(station.station_direction)
                positioned_point = station.positioned_point + k * positive_direction
                station_point_group.use("p" + str(serial_num), positioned_point)
        self.define(station_point_group)

    def def_station_name(self):
        station_name_chn_group = Group("station_name_chn").scale(LABEL_TEX_CHN_SCALE_FACTOR).set_style({
            "fill": LABEL_CHN_COLOR,
        })
        station_name_eng_group = Group("station_name").scale(LABEL_TEX_ENG_SCALE_FACTOR).set_style({
            "fill": LABEL_ENG_COLOR,
        })
        group_objs = (station_name_chn_group, station_name_eng_group)

        # This process writes tex_file and really takes long
        def build_tex_objs(station):
            tex_chn_obj = Tex(station.station_name_chn, LABEL_TEX_CHN_FONT_CMDS, LABEL_TEX_CHN_SCALE_FACTOR)
            tex_eng_obj = Tex(station.station_name, LABEL_TEX_ENG_FONT_CMDS, LABEL_TEX_ENG_SCALE_FACTOR)
            return (tex_chn_obj, tex_eng_obj)
        tex_objs_list = list(map(build_tex_objs, self.station_objs))

        align_buffs = (LABEL_BUFF_BIG, LABEL_BUFF_SMALL)
        line_buff = LABEL_BUFF_BETWEEN_LINES
        for station, tex_objs in zip(self.station_objs, tex_objs_list):
            aligned_direction = station.aligned_direction
            align_buff = align_buffs[get_simplified_direction(aligned_direction) % 2]
            aligned_point = station.aligned_point - aligned_direction * align_buff
            tex_box = TexBox(tex_objs, aligned_point, aligned_direction, line_buff)
            self.append_tex_box_to_groups_seperately(tex_objs, tex_box, group_objs)
            
        self.define(station_name_chn_group)
        self.define(station_name_eng_group)

    def def_station_name_shadow(self):
        station_name_shadow_group = Group("station_name_shadow").set_style({
            "fill": None,
            "stroke": LABEL_SHADOW_COLOR,
            "stroke-width": LABEL_SHADOW_STROKE_WIDTH * 2 / TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": LABEL_SHADOW_OPACITY,
        })
        station_name_shadow_group.use("station_name_chn")
        station_name_shadow_group.use("station_name")
        self.define(station_name_shadow_group)


    def create_project(self):
        self.draw(
            "geometric_map",
            "group1",#
            "route",
            "station_frame",
            "station_point"
        )
        self.write_tex(
            "station_name_shadow",
            "station_name",
            "station_name_chn"
        )
        
