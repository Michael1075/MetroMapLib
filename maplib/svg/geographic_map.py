import numpy as np

import maplib.constants as consts

from maplib.svg.geography import Geography
from maplib.svg.geography import Island
from maplib.svg.geography import Lake
from maplib.svg.geography import Land
from maplib.svg.geography import River
from maplib.svg.geography import RoundLake
from maplib.tools.position import position
from maplib.tools.position import position_list


class Shanghai(Land):
    def __init__(self):
        control_points = position_list(
            [260, 300],
            [380, 180],
            [380, 18],
            [362, 0],
        )
        Land.__init__(self, "Shanghai", control_points, [consts.LD, consts.LU])


class ChongmingIsland(Land):
    def __init__(self):
        control_points = position_list(
            [332, 300],
            [364, 268],
            [400, 268],
        )
        Land.__init__(self, "Chongming_Island", control_points, [consts.RU])


class ChangxingIsland(Land):
    def __init__(self):
        control_points = position_list(
            [283, 300],
            [351, 232],
            [362, 232],
            [362, 247],
            [309, 300],
        )
        Land.__init__(self, "Changxing_Island", control_points)


class HengshaIsland(Island):
    def __init__(self):
        control_points = position_list(
            [368, 242],
            [368, 220],
            [386, 220],
            [386, 242],
        )
        Island.__init__(self, "Hengsha_Island", control_points)


class HuangpuRiver(River):
    def __init__(self):
        control_points = position_list(
            [0, 95],
            [18, 95],
            [58, 55],
            [162, 55],
            [162, 70],
            [173, 81],
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
        River.__init__(self, "Huangpu_River", control_points)


class SuzhouCreek(River):
    def __init__(self):
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
        River.__init__(self, "Suzhou_Creek", control_points)


class DianshanLake(Lake):
    def __init__(self):
        control_points = position_list(
            [0, 186],
            [12, 186],
            [12, 164],
            [0, 152],
        )
        Lake.__init__(self, "Dianshan_Lake", control_points)


class DishuiLake(RoundLake):
    def __init__(self):
        RoundLake.__init__(self, "Dishui_Lake", 5.0, position(370, 26))


class GeograpicMap(Geography):
    def add_components(self):
        self.land_group.append(Shanghai())
        self.land_group.append(ChongmingIsland())
        self.land_group.append(ChangxingIsland())
        self.land_group.append(HengshaIsland())
        self.river_group.append(HuangpuRiver())
        self.river_group.append(SuzhouCreek())
        self.lake_group.append(DianshanLake())
        self.lake_group.append(DishuiLake())

