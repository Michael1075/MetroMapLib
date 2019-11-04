import numpy as np

from constants import *
from parameters import LAND_COLOR
from parameters import WATER_AREA_COLOR

from svg.svg_composite import BackgroundRectangle
from svg.svg_composite import Island
from svg.svg_composite import Lake
from svg.svg_composite import Land
from svg.svg_composite import River
from svg.svg_element import Circle
from svg.svg_element import Group
from tools.config_ops import digest_locals
from tools.position import position
from tools.position import position_list


class GeograpicMap(Group):
    def __init__(self):
        Group.__init__(self, "geometric_map")
        self.background_rect()
        self.init_groups()
        self.shanghai()
        self.chongming_island()
        self.changxing_island()
        self.hengsha_island()
        self.huangpu_river()
        self.suzhou_creek()
        self.dishui_lake()
        self.district_and_water_name()

    def background_rect(self):
        background_rect_obj = BackgroundRectangle("background_rect")
        self.append(background_rect_obj)

    def init_groups(self):
        land_group = Group("land").set_style({
            "fill": LAND_COLOR,
        })
        river_group = Group("river").set_style({
            "fill": None,
            "stroke": WATER_AREA_COLOR,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        lake_group = Group("lake").set_style({
            "fill": WATER_AREA_COLOR,
        })
        digest_locals(self)
        self.append(land_group)
        self.append(river_group)
        self.append(lake_group)

    def shanghai(self):
        control_points = position_list(
            [260, 300],
            [380, 180],
            [380, 18],
            [362, 0],
        )
        shanghai_obj = Land("Shanghai", control_points, [LD, LU])
        self.land_group.append(shanghai_obj)

    def chongming_island(self):
        control_points = position_list(
            [332, 300],
            [364, 268],
            [400, 268],
        )
        chongming_island_obj = Land("Chongming_Island", control_points, [RU])
        self.land_group.append(chongming_island_obj)

    def changxing_island(self):
        control_points = position_list(
            [283, 300],
            [351, 232],
            [362, 232],
            [362, 247],
            [309, 300],
        )
        changxing_island_obj = Land("Changxing_Island", control_points)
        self.land_group.append(changxing_island_obj)

    def hengsha_island(self):
        control_points = position_list(
            [368, 242],
            [368, 220],
            [386, 220],
            [386, 242],
        )
        hengsha_island_obj = Island("Hengsha_Island", control_points)
        self.land_group.append(hengsha_island_obj)

    def huangpu_river(self):
        control_points = position_list(
            [0, 60],
            [162, 60],
            [162, 75],
            [173, 86],
            [173, 114],
            [185, 126],
            [185, 141],
            [194, 150],
            [215, 150],
            [221, 156],
            [221, 186],
            [282, 186],
            [282, 244],
            [248, 278],
            [265, 295],
        )
        huangpu_river_obj = River("Huangpu_River", control_points)
        self.river_group.append(huangpu_river_obj)

    def suzhou_creek(self):
        control_points = position_list(
            [0, 246],
            [64, 246],
            [110, 200],
            [158, 200],
            [165, 207],
            [187, 207],
            [187, 197],
            [230, 197],
            [230, 188.5],
        )
        suzhou_creek_obj = River("Suzhou_Creek", control_points)
        self.river_group.append(suzhou_creek_obj)

    def dishui_lake(self):
        dishui_lake_obj = Lake("Dishui_Lake", 5.0, position(370, 26))
        self.lake_group.append(dishui_lake_obj)

    def district_and_water_name(self):
        pass

