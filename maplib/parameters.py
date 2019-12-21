from functools import reduce
import json
import operator as op
import os

import maplib.constants as consts

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


# dirs
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_DIR = os.path.join(THIS_DIR, "files")
INPUT_FILES_FOLDER_DIR = os.path.join(FILE_DIR, "input_files")
OUTPUT_FILES_FOLDER_DIR = os.path.join(FILE_DIR, "output_files")
TEX_CACHE_DIR = os.path.join(FILE_DIR, "tex_cache")
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
OPEN_OUTPUT_FILE_AT_ONCE = True
PRINT_TEX_WRITING_PROGRESS_MSG = True
PRINT_SVG_MODIFYING_MSG = True
PRINT_FILE_READY_MSG = True
PRINT_TIMER_MSG = True

# msgs
TEX_WRITING_PROGRESS_MSG = "Writing '{0}' to {1}"
SINGLE_TEX_MSG = "{0} {1} - {2}"
GENERATE_SUCCESSFULLY_MSG = "Successfully generated"
GENERATE_UNSUCCESSFULLY_MSG = "Already existed"
REMOVE_SUCCESSFULLY_MSG = "Successfully removed"
REMOVE_UNSUCCESSFULLY_MSG = "Does not exist"
TEX_GENERATE_MEG = "Generating tex..."
TEX_REMOVE_MEG = "Removing tex..."
SVG_INITIALIZE_MSG = "Initializing json..."
SVG_COPY_MSG = "Copying json..."
SVG_COPY_FINISH_MSG = "Successfully copied to {0}"
FILE_READY_MSG = "File ready at {0}"
TIMER_MSG = "Consumed time of function {0}: {1:.3f} second(s)"

# size
FULL_WIDTH = 490.0
FULL_HEIGHT = 400.0
FULL_SIZE = np_float(FULL_WIDTH, FULL_HEIGHT)
BODY_WIDTH = 450.0
BODY_HEIGHT = 320.0
BODY_SIZE = np_float(BODY_WIDTH, BODY_HEIGHT)

# composition
MAP_GROUP_SHIFT_VECTOR = np_float(20.0, 40.0)
MAP_BODY_SHIFT_VECTOR = np_float(20.0, 0.0)
GRADIENT_WIDTH = 20.0
GRADIENT_HEIGHT = 20.0
MAIN_COLOR = consts.WHITE

# mask
MASK_BASE_COLOR = consts.WHITE
MASK_COLOR = consts.BLACK

# tex
TEX_FONT_CMDS_DICT = {
    consts.CHN: ("songti", "heiti", "lishu", "youyuan"),
    consts.ENG: ("rmfamily", "sffamily"),
}
TEX_FONT_CMDS = reduce(op.add, TEX_FONT_CMDS_DICT.values())
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
BODY_RADIUS_DICT = {
    "normal": 0.4,
    "interchange": 0.55
}
BODY_STROKE_WIDTH_DICT = {
    "normal": 0.2,
    "interchange": 0.1
}
BODY_STROKE_OPACITY = 0.9
BODY_FILL_COLOR = consts.WHITE
INTERCHANGE_STATION_BODY_STROKE_COLOR = consts.BLACK

# svg paths
METRO_LOGO_INFO = {
    "svg_dir": os.path.join(INPUT_FILES_FOLDER_DIR, "shanghai_metro_logo.svg"),
    "scale_factor": 15.0,
    "aligned_point": np_float(20, 380),
    "color": Color(215, 5, 8)
}

# geography colors
LAND_COLOR = consts.WHITE
WATER_AREA_COLOR = Color(217, 235, 247)

# tex colors
STATION_NAME_MAIN_COLOR = consts.BLACK
STATION_NAME_SUB_COLOR = Color(140, 140, 140)
STATION_NAME_SHADOW_COLOR = consts.WHITE
DISTRICT_NAME_COLOR = Color(120, 120, 120)
WATER_AREA_NAME_COLOR = Color(93, 188, 218)

# tex style
STATION_NAME_TEX_STYLE = {
    "small_buff": 0.1,
    "big_buff": 0.3,
    "tex_box_format": consts.VERTICAL,
    "tex_buff": -0.2,
    "languages": {
        consts.CHN: {
            "exists": True,
            "tex_box_index": 0,
            "scale_factor": 1.4,
            "font_cmd": "youyuan",
            "color": STATION_NAME_MAIN_COLOR,
        },
        consts.ENG: {
            "exists": True,
            "tex_box_index": 1,
            "scale_factor": 1.0,
            "font_cmd": "sffamily",
            "color": STATION_NAME_SUB_COLOR,
        },
    },
    "shadow": {
        "color": STATION_NAME_SHADOW_COLOR,
        "stroke_width": 0.07,
        "opacity": 0.7,
    },
}
GEOGRAPHIC_NAME_TEX_STYLE = {
    "district_name": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "languages": {
            consts.CHN: {
                "exists": True,
                "tex_box_index": 0,
                "scale_factor": 2.5,
                "font_cmd": "songti",
                "color": DISTRICT_NAME_COLOR,
            },
            consts.ENG: {
                "exists": True,
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_cmd": "rmfamily",
                "color": DISTRICT_NAME_COLOR,
            },
        },
    },
    "river_name": {
        "tex_box_format": consts.HORIZONTAL,
        "tex_buff": 1.0,
        "languages": {
            consts.CHN: {
                "exists": True,
                "tex_box_index": 0,
                "scale_factor": 2.0,
                "font_cmd": "songti",
                "color": WATER_AREA_NAME_COLOR,
            },
            consts.ENG: {
                "exists": True,
                "tex_box_index": 1,
                "scale_factor": 2.0,
                "font_cmd": "rmfamily",
                "color": WATER_AREA_NAME_COLOR,
            },
        },
    },
    "lake_name": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "languages": {
            consts.CHN: {
                "exists": True,
                "tex_box_index": 0,
                "scale_factor": 2.2,
                "font_cmd": "songti",
                "color": WATER_AREA_NAME_COLOR,
            },
            consts.ENG: {
                "exists": True,
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_cmd": "rmfamily",
                "color": WATER_AREA_NAME_COLOR,
            },
        },
    },
}

