from attributes import *

from constants import *

from mobject.composite_mobject import Route


class River(Route):
    CONFIG = {
        "arc_radius": RIVER_ARC_RADIUS,
        "stroke_width": RIVER_STROKE_WIDTH,
        "color": RIVER_COLOR,
    }
