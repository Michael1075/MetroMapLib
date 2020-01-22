from maplib.svg.canvas import Canvas
from maplib.svg.geographic_map import GeographicMap
from maplib.svg.tex_instance import Compass
from maplib.svg.tex_instance import GeographicName
from maplib.svg.tex_instance import MapInfo
from maplib.svg.tex_instance import MarkGroup
from maplib.svg.tex_instance import SignName
from maplib.svg.tex_instance import StationName
from maplib.svg.misc import BodyMaskRectangle
from maplib.svg.misc import BodyRectangle
from maplib.svg.misc import FullRectangle
from maplib.svg.misc import Grid
from maplib.svg.misc import MapFrame
from maplib.svg.misc import MaskRectangle
from maplib.svg.misc import SidePart
from maplib.svg.svg_element import Group
from maplib.svg.web_system import WebSystem
from maplib.utils.constructor import Constructor


class MapBody(Group, Constructor):
    def __init__(self, id_name):
        Constructor.__init__(self)
        Group.__init__(self, id_name)
        self.shift(self.params.MAP_BODY_SHIFT_VECTOR)
        components = self.get_components()
        for component in components:
            self.append(component)

    def get_components(self):
        return (
            GeographicMap("geographic_map", self.geography_objs_dict),
            GeographicName("geographic_name", self.name_objs_dict),
            WebSystem("web_system", self.metro_objs, self.station_objs),
            StationName("station_name", self.station_objs),
            SignName("sign_name", self.metro_objs),
            MarkGroup("mark_group", self.mark_objs_dict),
            Compass("compass"),
        )


class MapGroup(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.shift(self.params.MAP_GROUP_SHIFT_VECTOR)
        components = self.get_components()
        for component in components:
            self.append(component)

    def get_components(self):
        return (
            MapBody("map_body"),
            Grid("grid"),
            MapFrame("map_frame"),
        )


class ProjectGroup(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.init_template()
        template_components = self.get_template_components()
        for component in template_components:
            self.template.append(component)
        components = self.get_components()
        for component in components:
            self.append(component)

    def get_template_components(self):
        return (
            BodyRectangle("body_rect"),
            FullRectangle("full_rect"),
            BodyMaskRectangle("body_mask_rect"),
            MaskRectangle("mask_rect"),
        )

    def get_components(self):
        return (
            MapGroup("map_group"),
            SidePart("side_part"),
            MapInfo("map_info"),
        )


class Project(Canvas):
    def construct(self):
        self.define(ProjectGroup("project"))
        self.draw("project")
