from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeograpicMap
from maplib.svg.tex_instance import DistrictName
from maplib.svg.tex_instance import LakeName
from maplib.svg.tex_instance import RiverName
from maplib.svg.tex_instance import StationName
from maplib.svg.misc import FrameRectangle
from maplib.svg.misc import Grid
from maplib.svg.misc import ShanghaiMetroLogo
from maplib.svg.svg_element import Group
from maplib.svg.web_system import WebSystem
from maplib.utils.constructor import Constructor


class Project(Constructor, Canvas):
    def __init__(self, input_file, output_file):
        Constructor.__init__(self, input_file)
        Canvas.__init__(self, output_file)

    def construct(self):
        self.def_frame_rect()
        self.def_map_group()
        self.def_shanghai_metro_logo()
        self.draw_components()

    def def_frame_rect(self):
        frame_rect = FrameRectangle("frame_rect")
        self.define(frame_rect)

    def def_map_group(self):
        geographic_map = GeograpicMap("geographic_map")
        grid = Grid("grid")
        web_system = WebSystem("web_system", self.metro_objs, self.station_objs)
        station_name = StationName("station_name", self.station_objs)
        district_name = DistrictName("district_name", self.district_name_objs)
        river_name = RiverName("river_name", self.river_name_objs)
        lake_name = LakeName("lake_name", self.lake_name_objs)
        map_group = Group("map_group")
        map_group.append(geographic_map)
        map_group.append(grid)
        map_group.append(web_system)
        map_group.append(station_name)
        map_group.append(district_name)
        map_group.append(river_name)
        map_group.append(lake_name)
        self.define(web_system.template_group)
        self.define(map_group)

    def def_shanghai_metro_logo(self):
        shanghai_metro_logo = ShanghaiMetroLogo("Shanghai_metro_logo")
        self.define(shanghai_metro_logo)

    def draw_components(self):
        self.draw("frame_rect")
        self.draw("map_group")
        self.draw("Shanghai_metro_logo")

