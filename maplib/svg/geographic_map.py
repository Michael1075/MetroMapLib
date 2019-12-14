import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Circle
from maplib.svg.svg_element import Group
from maplib.tools.assertions import assert_length
from maplib.tools.config_ops import digest_locals
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import unify_vector


class Land(LPath):
    attrs_needed = 2
    has_branch = True
    group_name = "land_group"

    def __init__(self, id_name, arc_radius, control_points, corner_control_points):
        LPath.__init__(self, id_name, control_points, arc_radius)
        for corner_control_point in corner_control_points:
            self.line_to(corner_control_point)
        self.close_path()
        self.finish_path()


class Island(OPath):
    attrs_needed = 2
    has_branch = False
    group_name = "land_group"

    def __init__(self, id_name, arc_radius, control_points):
        OPath.__init__(self, id_name, control_points, arc_radius)


class River(YPath):
    attrs_needed = 3
    has_branch = False
    group_name = "river_group"

    def __init__(self, id_name, arc_radius, river_width, control_points):
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
        last_right_point = rotate(former_point, consts.PI / 2, middle_point)
        last_left_point = rotate(former_point, -consts.PI / 2, middle_point)
        main_control_points = self.control_points[:-1]
        main_control_points.extend([middle_point, last_right_point])
        sub_control_points = [former_point, middle_point, last_left_point]
        return main_control_points, sub_control_points


class Lake(Land):
    group_name = "lake_group"


class InnerLake(Island):
    group_name = "lake_group"


class GeographicMap(Group):
    def __init__(self, id_name, geometry_data_dict):
        Group.__init__(self, id_name)
        self.geometry_data_dict = geometry_data_dict
        self.add_background_rect()
        self.init_groups()
        self.add_components()

    def add_background_rect(self):
        self.use_with_style("frame_rect", {
            "fill": params.WATER_AREA_COLOR,
        }, -params.MAIN_MAP_SHIFT_VECTOR)
        return self

    def init_groups(self):
        land_group = Group("land")
        land_group.set_style({
            "fill": params.LAND_COLOR,
        })
        river_group = Group("river")
        river_group.set_style({
            "fill": None,
            "stroke": params.WATER_AREA_COLOR,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        lake_group = Group("lake")
        lake_group.set_style({
            "fill": params.WATER_AREA_COLOR,
        })
        digest_locals(self)
        self.append(land_group)
        self.append(river_group)
        self.append(lake_group)
        return self

    def add_components(self):
        for obj_type, obj_list in self.geometry_data_dict.items():
            ClassType = eval(obj_type)
            for basic_data, detailed_data in obj_list:
                assert_length(basic_data, ClassType.attrs_needed)
                if ClassType.has_branch:
                    obj = self.get_component_with_branch(ClassType, basic_data, detailed_data)
                else:
                    obj = self.get_component(ClassType, basic_data, detailed_data)
                group = self.__getattribute__(ClassType.group_name)
                group.append(obj)
        return self

    def get_component_with_branch(self, ClassName, basic_data, detailed_data):
        signs = []
        coords = []
        for single_point_data in detailed_data:
            sign, x_coord, y_coord = single_point_data
            coord = np_float(x_coord, y_coord)
            signs.append(sign)
            coords.append(coord)
        branch_index = signs.index("#") + 1
        control_points = coords[:branch_index]
        corner_control_points = coords[branch_index:]
        obj = ClassName(*basic_data, control_points, corner_control_points)
        return obj

    def get_component(self, ClassName, basic_data, detailed_data):
        control_points = []
        for single_point_data in detailed_data:
            x_coord, y_coord = single_point_data
            coord = np_float(x_coord, y_coord)
            control_points.append(coord)
        obj = ClassName(*basic_data, control_points)
        return obj

