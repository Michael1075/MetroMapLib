import maplib.parameters as params

from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeographicMap
from maplib.svg.tex_instance import GeographicName
from maplib.svg.tex_instance import StationName
from maplib.svg.misc import FrameRectangle
from maplib.svg.misc import FullRectangle
from maplib.svg.misc import GradientFrame
from maplib.svg.misc import Grid
from maplib.svg.misc import MapFrame
from maplib.svg.misc import SidePart
from maplib.svg.misc import ShanghaiMetroLogo
from maplib.svg.svg_element import Group
from maplib.svg.web_system import WebSystem
from maplib.utils.constructor import Constructor


class Project(Constructor, Canvas):
    def __init__(self, metro_input_file, geography_input_file, output_file):
        Constructor.__init__(self, metro_input_file, geography_input_file)
        Canvas.__init__(self, output_file)

    def construct(self):
        self.def_rects()
        self.def_gradient_frame()
        self.def_map_group()
        self.def_side_part()
        self.def_shanghai_metro_logo()
        self.draw_components()

    def def_rects(self):
        frame_rect = FrameRectangle("frame_rect")
        full_rect = FullRectangle("full_rect")
        self.define(frame_rect)
        self.define(full_rect)

    def def_gradient_frame(self):
        gradient_frame = GradientFrame("gradient_frame")
        gradient_frame.append_components()
        self.define(gradient_frame)

    def def_map_group(self):
        geographic_map = GeographicMap("geographic_map", self.geometry_data_dict)
        geographic_name = GeographicName("geographic_name", self.name_objs_dict)
        web_system = WebSystem("web_system", self.metro_objs, self.station_objs)
        station_name = StationName("station_name", self.station_objs)
        map_frame = MapFrame("map_frame")
        grid = Grid("grid")
        
        map_body = Group("map_body")
        map_body.shift(params.MAIN_MAP_SHIFT_VECTOR)
        map_body.append(geographic_map)
        map_body.append(geographic_name)
        map_body.append(web_system)
        map_body.append(station_name)

        map_group = Group("map_group")
        map_group.shift(params.MAIN_FRAME_SHIFT_VECTOR)
        map_group.append(map_body)
        map_group.append(grid)
        map_group.append(map_frame)

        self.define(web_system.template_group)
        self.define(map_group)

    def def_side_part(self):
        side_part = SidePart("side_part")
        self.define(side_part.mask)
        self.define(side_part)

    def def_shanghai_metro_logo(self):
        shanghai_metro_logo = ShanghaiMetroLogo("Shanghai_metro_logo")
        self.define(shanghai_metro_logo)

    def draw_components(self):
        self.draw("map_group")
        self.draw("side_part")
        self.draw("Shanghai_metro_logo")

