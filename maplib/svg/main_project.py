import maplib.parameters as params

from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeographicMap
from maplib.svg.tex_instance import GeographicName
from maplib.svg.tex_instance import SignName
from maplib.svg.tex_instance import StationName
from maplib.svg.misc import BodyRectangle
from maplib.svg.misc import FullRectangle
from maplib.svg.misc import Grid
from maplib.svg.misc import MapFrame
from maplib.svg.misc import SidePart
from maplib.svg.misc import ShanghaiMetroLogo
from maplib.svg.svg_element import Group
from maplib.svg.web_system import WebSystem
from maplib.utils.constructor import Constructor


class MapBody(Group, Constructor):
    def __init__(self, id_name):
        Constructor.__init__(self)
        Group.__init__(self, id_name)
        self.shift(params.MAP_BODY_SHIFT_VECTOR)
        components = self.get_components()
        for component in components:
            self.append(component)

    def get_components(self):
        return (
            GeographicMap("geographic_map", self.geography_data_dict),
            GeographicName("geographic_name", self.name_objs_dict),
            WebSystem("web_system", self.metro_objs, self.station_objs),
            StationName("station_name", self.station_objs),
            SignName("sign_name", self.metro_objs),
        )


class MapGroup(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.shift(params.MAP_GROUP_SHIFT_VECTOR)
        components = self.get_components()
        for component in components:
            self.append(component)

    def get_components(self):
        return (
            MapBody("map_body"),
            Grid("grid"),
            MapFrame("map_frame"),
        )


class Project(Canvas):
    def construct(self):
        components = self.get_components()
        for component in components:
            self.define(component)
        self.draw_components()

    def get_components(self):
        return (
            BodyRectangle("body_rect"),
            FullRectangle("full_rect"),
            MapGroup("map_group"),
            SidePart("side_part"),
            ShanghaiMetroLogo("Shanghai_metro_logo"),
        )

    def draw_components(self):
        self.draw("map_group")
        self.draw("side_part")
        self.draw("Shanghai_metro_logo")
