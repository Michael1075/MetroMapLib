from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeograpicMap
from maplib.svg.tex_instance import DistrictName
from maplib.svg.tex_instance import LakeName
from maplib.svg.tex_instance import RiverName
from maplib.svg.tex_instance import StationName
from maplib.svg.misc import FrameRectangle
from maplib.svg.misc import Grid
from maplib.svg.misc import ShanghaiMetroLogo
from maplib.svg.web_system import WebSystem
from maplib.utils.constructor import Constructor


class Project(Canvas, Constructor):
    def __init__(self, input_file, output_file):
        Constructor.__init__(self, input_file)
        Canvas.__init__(self, output_file)

    def construct(self):
        self.config(FrameRectangle, "frame_rect")
        self.config(GeograpicMap, "geographic_map")
        self.config(Grid, "grid")
        self.config(WebSystem, "web_system", self.metro_objs, self.station_objs)
        self.config(StationName, "station_name", self.station_objs)
        self.config(DistrictName, "district_name", self.district_name_objs)
        self.config(RiverName, "river_name", self.river_name_objs)
        self.config(LakeName, "lake_name", self.lake_name_objs)
        self.config(ShanghaiMetroLogo, "Shanghai_metro_logo")

