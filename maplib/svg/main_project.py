from maplib.constants import *#
from maplib.parameters import *#

from maplib.svg.canva import Canva
from maplib.svg.geographic_map import GeograpicMap
from maplib.svg.svg_element import Group#
from maplib.svg.svg_element import Path#
from maplib.svg.tex_instance import StationName
from maplib.svg.web_system import WebSystem
from maplib.tools.position import position#
from maplib.tools.svg_file_tools import svg_to_pdf
from maplib.utils.color import Color#
from maplib.utils.constructor import MetroBuilder
from maplib.utils.constructor import StationBuilder


class Project(Canva):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        Canva.__init__(self, output_file)

    def construct(self):
        self.load_data()
        self.def_geographic_map()
        self.def_web()#
        self.def_web_system()
        self.def_station_name()
        self.draw_components()

    def load_data(self):
        metro_builder = MetroBuilder(self.input_file)
        station_data_dict = metro_builder.all_stations_data_dict
        station_builder = StationBuilder(station_data_dict)
        self.metro_objs = metro_builder.metros
        self.metro_objs.sort(key = lambda metro: metro.serial_num)
        self.station_objs = station_builder.stations

    def def_geographic_map(self):
        geographic_map_group = GeograpicMap("geographic_map")
        self.define(geographic_map_group)

    def def_web_system(self):
        web_system_group = WebSystem("web_system", self.metro_objs, self.station_objs)
        self.define(web_system_group.template_group)
        self.define(web_system_group)

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

        for i in range(50, 400, 50):
            group1.use("v", position(i, 0))
        for i in range(50, 300, 50):
            group1.use("h", position(0, i))

    def def_station_name(self):
        station_name_group = StationName("station_name", self.station_objs)
        self.define_tex(station_name_group)

    def draw_components(self):
        self.draw("geographic_map")
        self.draw("group1")#
        self.draw("web_system")
        self.draw("station_name")


class Main(Project):
    def __init__(self, input_file, output_file):
        if output_file.endswith(".svg"):
            Project(input_file, output_file)
        elif output_file.endswith(".pdf"):
            svg_output_file = output_file.replace(".pdf", ".svg")
            Project(input_file, svg_output_file)
            svg_to_pdf(svg_output_file, output_file)
        else:
            raise OSError

