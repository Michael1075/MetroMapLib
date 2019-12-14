import json
import os

import maplib.constants as consts

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


# dirs
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_DIR = os.path.join(THIS_DIR, "files")
INPUT_FILES_FOLDER_DIR = os.path.join(FILE_DIR, "input_files")
OUTPUT_FILES_FOLDER_DIR = os.path.join(FILE_DIR, "output_files")
TEX_DIR = os.path.join(FILE_DIR, "tex")
JSON_DIR = os.path.join(FILE_DIR, "json")
METRO_INPUT_FILE_DIR = os.path.join(INPUT_FILES_FOLDER_DIR, "metro_input.xlsx")
GEOGRAPHY_INPUT_FILE_DIR = os.path.join(INPUT_FILES_FOLDER_DIR, "geography_input.xlsx")
OUTPUT_FILE_DIR = os.path.join(OUTPUT_FILES_FOLDER_DIR, "output.svg")

# tex base
TEMPLATE_TEX_FILE = os.path.join(THIS_DIR, "tex_template.tex")
with open(TEMPLATE_TEX_FILE, "r") as input_file:
    TEMPLATE_TEX_FILE_BODY = input_file.read()
TEX_TO_REPLACE = "YourTextHere"

# json base
JSON_TEX_FILE_DEFAULT_DIR = os.path.join(JSON_DIR, "tex_file.json")
JSON_TEX_PATH_DEFAULT_DIR = os.path.join(JSON_DIR, "tex_path.json")
with open(JSON_TEX_FILE_DEFAULT_DIR, "r") as output_file:
    GLOBAL_FILE_DICT = json.load(output_file)
with open(JSON_TEX_PATH_DEFAULT_DIR, "r") as output_file:
    GLOBAL_PATH_DICT = json.load(output_file)

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
PRINT_TEX_WRITING_PROGRESS_MSG = True
PRINT_SVG_MODIFYING_MSG = True
PRINT_TIMER_MSG = True

# size
FULL_WIDTH = 490.0
FULL_HEIGHT = 400.0
FULL_SIZE = np_float(FULL_WIDTH, FULL_HEIGHT)
FRAME_WIDTH = 450.0
FRAME_HEIGHT = 320.0
FRAME_SIZE = np_float(FRAME_WIDTH, FRAME_HEIGHT)

# composition
MAIN_FRAME_SHIFT_VECTOR = np_float(20.0, 40.0)
MAIN_MAP_SHIFT_VECTOR = np_float(20.0, 0.0)
GRADIENT_WIDTH = 20.0
GRADIENT_HEIGHT = 20.0
MAIN_COLOR = consts.WHITE

# mask
MASK_BASE_COLOR = consts.WHITE
MASK_COLOR = consts.BLACK
GRADIENT_MASK_COLOR = consts.WHITE

# tex
TEX_FONT_CMDS_CHN = ("songti", "heiti", "lishu", "youyuan")
TEX_FONT_CMDS_ENG = ("rmfamily", "sffamily")
TEX_FONT_CMDS = TEX_FONT_CMDS_CHN + TEX_FONT_CMDS_ENG
TEX_BASE_SCALE_FACTOR = 0.07

# grid
GRID_STEP = 50.0
GRID_STROKE_WIDTH = 0.3
GRID_STROKE_OPACITY = 0.15
GRID_COLOR = Color(180, 180, 180)

# route
ROUTE_ARC_RADIUS = 2.0
ROUTE_STROKE_WIDTH = 0.8
ROUTE_MINOR_STROKE_WIDTH = 0.3
ROUTE_STROKE_OPACITY = 0.7

# station point
STATION_POINT_RADIUS = 0.4
STATION_POINT_FILL_OPACITY = 1.0

# station frame
FRAME_RADIUS_DICT = {
    "normal": 0.4,
    "interchange": 0.55
}
FRAME_STROKE_WIDTH_DICT = {
    "normal": 0.2,
    "interchange": 0.1
}
FRAME_STROKE_OPACITY = 0.9
FRAME_FILL_COLOR = consts.WHITE
INTERCHANGE_STATION_FRAME_STROKE_COLOR = consts.BLACK

# geography
LAND_COLOR = consts.WHITE
WATER_AREA_COLOR = Color(217, 235, 247)

# svg paths
METRO_LOGO_INFO = {
    "svg_dir": os.path.join(INPUT_FILES_FOLDER_DIR, "shanghai_metro_logo.svg"),
    "scale_factor": 15.0,
    "aligned_point": np_float(20, 380),
    "color": Color(215, 5, 8)
}

# tex style
STATION_NAME_TEX_STYLE = {
    "small_buff": 0.1,
    "big_buff": 0.3,
    "tex_box_format": consts.VERTICAL,
    "tex_buff": -0.2,
    "scale_factor": {
        "chn": 1.4,
        "eng": 1.0,
    },
    "font_cmd": {
        "chn": "youyuan",
        "eng": "sffamily",
    },
    "color": {
        "chn": consts.BLACK,
        "eng": Color(140, 140, 140),
    },
    "shadow": {
        "color": consts.WHITE,
        "stroke_width": 0.07,
        "opacity": 0.7,
    },
}
GEOGRAPHIC_NAME_TEX_STYLE = {
    "district_name": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "scale_factor": {
            "chn": 2.5,
            "eng": 1.4,
        },
        "font_cmd": {
            "chn": "songti",
            "eng": "rmfamily",
        },
        "color": Color(120, 120, 120),
    },
    "river_name": {
        "tex_box_format": consts.HORIZONTAL,
        "tex_buff": 1.0,
        "scale_factor": {
            "chn": 2.0,
            "eng": 2.0,
        },
        "font_cmd": {
            "chn": "songti",
            "eng": "rmfamily",
        },
        "color": Color(93, 188, 218),
    },
    "lake_name": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "scale_factor": {
            "chn": 2.2,
            "eng": 1.4,
        },
        "font_cmd": {
            "chn": "songti",
            "eng": "rmfamily",
        },
        "color": Color(93, 188, 218),
    },
}

