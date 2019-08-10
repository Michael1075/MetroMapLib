import numpy as np

from constants import *

"""
Global the data.
dict_key: a tuple which implies a coordinate
dict_value: tuple(
    the color of the corresponding point,
    station_name,
    station_name_chn,
    label_direction
)
"""
global_station_data_dict = {}


POINTS_PER_UNIT = 1

BACKGROUND_COLOR = WHITE #
FRAME_FILL_COLOR = WHITE # BLACK for text, WHITE for text stroke

ARC_RADIUS = 2.0
ROUTE_STROKE_WIDTH = 0.8
ROUTE_STROKE_OPACITY = 0.8 ###frame is child of Route...
STATION_POINT_RADIUS = 0.4
STATION_POINT_FILL_OPACITY = 1.0 ###?
FRAME_RADIUS_DICT = {"normal": 0.3, "interchange": 0.5}
FRAME_STROKE_WIDTH_DICT = {"normal": 0.4, "interchange": 0.2}

HAS_LABEL = True #
CHN_UP = True
LABEL_FONT_FACE = "Helvetica"
LABEL_FONT_FACE_CHN = "STXihei"
LABEL_FONT_SIZE = (1.2, 0.7)
LABEL_STROKE_WIDTH = 1.0 ###
LABEL_STROKE_COLOR = BLACK # test??
LABEL_TEXT_COLOR = (BLACK, GREY) # test
STATION_LABEL_BUFF = np.array([0.2, 0.2])

RIVER_COLOR = BLUE_A
RIVER_ARC_RADIUS = 4.0
RIVER_STROKE_WIDTH = 2.0

