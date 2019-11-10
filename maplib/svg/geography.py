from maplib.constants import *
from maplib.parameters import *

from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Circle
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Rectangle
from maplib.tools.config_ops import digest_locals
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import unify_vector


class BackgroundRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name)
        self.set_rect_size(SIZE)
        self.set_style({
            "fill": WATER_AREA_COLOR,
        })


class Land(LPath):
    def __init__(self, id_name, control_points, add_corners = None):
        arc_radius = COASTLINE_ARC_RADIUS
        LPath.__init__(self, id_name, control_points, arc_radius)
        if add_corners is not None:
            for corner in add_corners:
                corner_coord = (corner + RU) * SIZE / 2
                self.line_to(corner_coord)
        self.close_path()
        self.finish_path()


class Island(OPath):
    def __init__(self, id_name, control_points):
        arc_radius = COASTLINE_ARC_RADIUS
        OPath.__init__(self, id_name, control_points, arc_radius)


class River(YPath):
    def __init__(self, id_name, control_points):
        arc_radius = RIVER_ARC_RADIUS_DICT[id_name]
        river_width = RIVER_WIDTH_DICT[id_name]
        digest_locals(self)
        main_control_points, sub_control_points = self.compute_river_control_points()
        YPath.__init__(self, id_name, main_control_points, sub_control_points, arc_radius)
        self.set_style({
            "stroke-width": river_width,
        })

    def compute_river_control_points(self):
        last_given_point = self.control_points[-1]
        unit_vector = unify_vector(last_given_point - self.control_points[-2])
        middle_point = last_given_point + self.river_width * unit_vector / 2
        former_point = middle_point - self.arc_radius * unit_vector
        last_right_point = rotate(former_point, PI / 2, middle_point)
        last_left_point = rotate(former_point, -PI / 2, middle_point)
        main_control_points = self.control_points[:-1]
        main_control_points.extend([middle_point, last_right_point])
        sub_control_points = [former_point, middle_point, last_left_point]
        return main_control_points, sub_control_points


class Lake(Land):
    pass


class RoundLake(Circle):
    def __init__(self, id_name, radius, center_coord):
        Circle.__init__(self, id_name)
        self.set_radius(radius)
        self.set_circle_center_coord(center_coord)


class Geography(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        self.background_rect()
        self.init_groups()
        self.add_components()

    def background_rect(self):
        background_rect_obj = BackgroundRectangle("background_rect")
        self.append(background_rect_obj)
        return self

    def init_groups(self):
        land_group = Group("land")
        land_group.set_style({
            "fill": LAND_COLOR,
        })
        river_group = Group("river")
        river_group.set_style({
            "fill": None,
            "stroke": WATER_AREA_COLOR,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        lake_group = Group("lake")
        lake_group.set_style({
            "fill": WATER_AREA_COLOR,
        })
        digest_locals(self)
        self.append(land_group)
        self.append(river_group)
        self.append(lake_group)
        return self

    def add_components(self):
        pass

