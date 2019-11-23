from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeograpicMap
from maplib.svg.svg_element import Group#
from maplib.svg.svg_element import Path#
from maplib.svg.tex_instance import DistrictName
from maplib.svg.tex_instance import StationName
from maplib.svg.tex_instance import WaterAreaName
from maplib.svg.misc import FrameRectangle
from maplib.svg.misc import ShanghaiMetroLogo
from maplib.svg.web_system import WebSystem
from maplib.tools.position import position#
from maplib.utils.color import Color#
from maplib.utils.constructor import Constructor


class Project(Canvas):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        Canvas.__init__(self, output_file)

    def construct(self):
        self.load_data()
        self.def_frame_rect()
        self.def_geographic_map()
        #self.def_web()#
        self.def_web_system()
        self.def_station_name()
        self.def_district_name()
        self.def_water_area_name()
        self.def_metro_logo()
        self.draw_components()

    def load_data(self):
        constructor = Constructor(self.input_file)
        self.metro_objs = constructor.metros
        self.station_objs = constructor.stations
        self.district_name_objs = constructor.district_names
        self.water_area_name_objs = constructor.water_area_names

    def def_frame_rect(self):
        frame_rect = FrameRectangle("frame_rect")
        self.define(frame_rect)

    def def_geographic_map(self):
        geographic_map_group = GeograpicMap("geographic_map")
        self.define(geographic_map_group)
    
    def def_web(self):#
        hpath = Path("h")
        hpath.move_to(position(0, 0)).h_line_to(400).finish_path()
        vpath = Path("v")
        vpath.move_to(position(0, 0)).v_line_to(300).finish_path()
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

    def def_web_system(self):
        web_system_group = WebSystem("web_system", self.metro_objs, self.station_objs)
        self.define(web_system_group.template_group)
        self.define(web_system_group)

    def def_station_name(self):
        station_name_group = StationName("station_name", self.station_objs)
        self.define_tex(station_name_group)

    def def_district_name(self):
        district_name_group = DistrictName("district_name", self.district_name_objs)
        self.define_tex(district_name_group)

    def def_water_area_name(self):
        water_area_name_group = WaterAreaName("water_area_name", self.water_area_name_objs)
        self.define_tex(water_area_name_group)

    def def_metro_logo(self):
        metro_logo = ShanghaiMetroLogo("Shanghai_metro_logo")
        self.define(metro_logo)

    def draw_components(self):
        self.draw("geographic_map")
        self.draw("group1")#
        self.draw("web_system")
        self.draw("station_name")
        self.draw("district_name")
        self.draw("water_area_name")
        self.draw("Shanghai_metro_logo")

