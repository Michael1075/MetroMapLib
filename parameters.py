import os

from constants import BLACK
from constants import WHITE

from tools.color import Color
from tools.position import position


# dirs
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_DIR = os.path.join(os.getenv("FILE_DIR", default = THIS_DIR), "files")
INPUT_FILE_NAME = os.path.join(FILE_DIR, "input_data.xlsx")
OUTPUT_FILE_NAME = os.path.join(FILE_DIR, "output_svg.svg")
TEX_DIR = os.path.join(FILE_DIR, "Tex")

# tex base
TEMPLATE_TEX_FILE = os.path.join(FILE_DIR, "tex_template.tex")
with open(TEMPLATE_TEX_FILE, "r") as infile:
    TEMPLATE_TEX_FILE_BODY = infile.read()
TEX_TO_REPLACE = "YourTextHere"

# svg base
SVG_VERSION = "1.1"
SVG_XMLNS = "http://www.w3.org/2000/svg"
SVG_XLINK = "http://www.w3.org/1999/xlink"
SVG_HEAD = "".join([
	'<?xml version="1.0" standalone="no"?>',
	'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
])

# base settings
DECIMAL_DIGITS = 6
TOLERANCE = 1e-8

# size
WIDTH = 400.0
HEIGHT = 300.0
SIZE = position(WIDTH, HEIGHT)

# tex
TEX_FONT_CMDS = ("heiti", "youyuan", "rmfamily", "sffamily", "ttfamily")
TEX_BASE_SCALE_FACTOR = 0.07
PRINT_TEX_WRITING_PROGRESS = True

# geography
COASTLINE_ARC_RADIUS = 6.0
RIVER_ARC_RADIUS_DICT = {"Huangpu_River": 6.0, "Suzhou_Creek": 2.4}
RIVER_WIDTH_DICT = {"Huangpu_River": 5.0, "Suzhou_Creek": 2.0}
LAND_COLOR = WHITE
WATER_AREA_COLOR = Color(199, 233, 241)

# route and station
ROUTE_ARC_RADIUS = 2.0
ROUTE_STROKE_WIDTH = 0.8
ROUTE_STROKE_OPACITY = 0.7
STATION_POINT_RADIUS = 0.4
STATION_POINT_FILL_OPACITY = 1.0
FRAME_RADIUS_DICT = {"normal": 0.4, "interchange": 0.55}
FRAME_STROKE_WIDTH_DICT = {"normal": 0.2, "interchange": 0.1}
FRAME_STROKE_OPACITY = 0.9
FRAME_FILL_COLOR = WHITE
INTERCHANGE_STATION_FRAME_STROKE_COLOR = BLACK

# label
LABEL_BUFF_SMALL = 0.1
LABEL_BUFF_BIG = 0.3
LABEL_BUFF_BETWEEN_LINES = -0.2
LABEL_TEX_CHN_SCALE_FACTOR = 1.4
LABEL_TEX_ENG_SCALE_FACTOR = 1.0
LABEL_TEX_CHN_FONT_CMDS = ("youyuan",)
LABEL_TEX_ENG_FONT_CMDS = ("sffamily",)
LABEL_CHN_COLOR = BLACK
LABEL_ENG_COLOR = Color(140, 140, 140)
LABEL_SHADOW_COLOR = WHITE
LABEL_SHADOW_STROKE_WIDTH = 0.07
LABEL_SHADOW_OPACITY = 0.7

