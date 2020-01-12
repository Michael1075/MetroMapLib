import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.path_types import LPath
from maplib.svg.path_types import OPath
from maplib.svg.path_types import YPath
from maplib.svg.svg_element import Group
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.space_ops import rotate
from maplib.tools.space_ops import unify_vector


class Land(LPath):
    has_branch = True
    group_name = "land_group"

    def __init__(self, id_name, control_points, corner_control_points, arc_radius):
        LPath.__init__(self, id_name, control_points, arc_radius)
        for corner_control_point in corner_control_points:
            self.line_to(corner_control_point)
        self.close_path()
        self.finish_path()


class Island(OPath):
    has_branch = False
    group_name = "land_group"

    def __init__(self, id_name, control_points, arc_radius):
        OPath.__init__(self, id_name, control_points, arc_radius)


class River(YPath):
    has_branch = False
    group_name = "river_group"

    def __init__(self, id_name, control_points, arc_radius, river_width):
        self.control_points = control_points
        self.arc_radius = arc_radius
        self.river_width = river_width
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
    def __init__(self, id_name, geography_data_dict):
        Group.__init__(self, id_name)
        self.geography_data_dict = geography_data_dict
        self.add_background_rect()
        group_dict = GeographicMap.get_group_dict()
        for group in group_dict.values():
            self.append(group)
        self.group_dict = group_dict
        self.add_components()

    def add_background_rect(self):
        self.use_with_style("body_rect", {
            "fill": params.GEOGRAPHY_COLORS["water_area"],
        }, -params.MAP_BODY_SHIFT_VECTOR)
        return self

    @staticmethod
    def get_group_dict():
        land_group = Group("land")
        land_group.set_style({
            "fill": params.GEOGRAPHY_COLORS["land"],
        })
        river_group = Group("river")
        river_group.set_style({
            "fill": None,
            "stroke": params.GEOGRAPHY_COLORS["water_area"],
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        lake_group = Group("lake")
        lake_group.set_style({
            "fill": params.GEOGRAPHY_COLORS["water_area"],
        })
        return {
            "land_group": land_group,
            "river_group": river_group,
            "lake_group": lake_group,
        }

    def add_components(self):
        for obj_type, obj_tuple in self.geography_data_dict.items():
            ClassName = eval(obj_type)
            for obj_dict, obj_data in obj_tuple:
                obj_name = obj_dict.pop("name")
                if ClassName.has_branch:
                    obj = GeographicMap.get_component_with_branch(
                        ClassName, obj_name, obj_dict, obj_data
                    )
                else:
                    obj = GeographicMap.get_component(
                        ClassName, obj_name, obj_dict, obj_data
                    )
                self.group_dict[ClassName.group_name].append(obj)
        return self

    @staticmethod
    def get_component_with_branch(ClassName, obj_name, obj_attr_dict, obj_data):
        coords = []
        signs = []
        for single_point_data in obj_data:
            x_coord, y_coord, sign = single_point_data
            coord = np_float(x_coord, y_coord)
            coords.append(coord)
            signs.append(sign)
        branch_index = signs.index("#") + 1
        control_points = coords[:branch_index]
        corner_control_points = coords[branch_index:]
        obj = ClassName(obj_name, control_points, corner_control_points, **obj_attr_dict)
        return obj

    @staticmethod
    def get_component(ClassName, obj_name, obj_attr_dict, obj_data):
        control_points = []
        for single_point_data in obj_data:
            x_coord, y_coord = single_point_data
            coord = np_float(x_coord, y_coord)
            control_points.append(coord)
        obj = ClassName(obj_name, control_points, **obj_attr_dict)
        return obj
