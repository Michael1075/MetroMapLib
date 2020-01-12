from functools import reduce
import json
import operator as op
import os

import maplib.constants as consts

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


# project name
PROJECT_CITY_NAME = "Shanghai"

# dirs
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_DIR = os.path.join(THIS_DIR, "files")
PROJECT_DIR = os.path.join(FILE_DIR, PROJECT_CITY_NAME)
TEX_CACHE_DIR = os.path.join(FILE_DIR, "tex_cache")
INPUT_JSON_DIR = os.path.join(PROJECT_DIR, "input.json")
METRO_LOGO_DIR = os.path.join(PROJECT_DIR, "metro_logo.svg")
TEX_JSON_DIR = os.path.join(PROJECT_DIR, "tex.json")
OUTPUT_SVG_DIR = os.path.join(PROJECT_DIR, "output.svg")

# load database
with open(INPUT_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
    INPUT_DATABASE_DICT = json.load(input_file)

# tex base
TEMPLATE_TEX_FILE = os.path.join(FILE_DIR, "tex_template.tex")
with open(TEMPLATE_TEX_FILE, "r") as input_file:
    TEMPLATE_TEX_FILE_BODY = input_file.read()
TEX_TO_REPLACE = "YourTextHere"
with open(TEX_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
    GLOBAL_TEX_DICT = json.load(input_file)

# svg base
SVG_VERSION = "1.1"
SVG_XMLNS = "http://www.w3.org/2000/svg"
SVG_XLINK = "http://www.w3.org/1999/xlink"

# base settings
DECIMAL_DIGITS = 6
TOLERANCE = 1e-8
OPEN_OUTPUT_FILE_AT_ONCE = True
PRINT_TEX_WRITING_PROGRESS_MSG = True
PRINT_FILE_MODIFYING_MSG = True
PRINT_FILE_READY_MSG = True
PRINT_TIMER_MSG = True

# msgs
TEX_WRITING_PROGRESS_MSG = "Writing '{0}'"
SINGLE_TEX_MSG = "{0} - {1}"
GENERATE_SUCCESSFULLY_MSG = "Successfully generated"
GENERATE_UNSUCCESSFULLY_MSG = "Already existed"
REMOVE_SUCCESSFULLY_MSG = "Successfully removed"
REMOVE_UNSUCCESSFULLY_MSG = "Does not exist"
TEX_GENERATE_MEG = "Generating tex..."
TEX_REMOVE_MEG = "Removing tex..."
INITIALIZE_MSG = "Initializing {0}..."
COPY_MSG = "Copying {0}..."
COPY_FINISH_MSG = "Successfully copied to {0}"
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

# mask
MASK_BASE_COLOR = consts.WHITE
MASK_COLOR = consts.BLACK

# tex
TEX_FONT_CMDS_DICT = {
    consts.CHN: ("songti", "heiti", "lishu", "youyuan", "kaishu", "fangsong"),
    consts.ENG: ("rmfamily", "sffamily", "ttfamily"),
}
TEX_FONT_CMDS = reduce(op.add, TEX_FONT_CMDS_DICT.values())
TEX_BASE_SCALE_FACTOR = 0.07

# colors
MAIN_COLOR = consts.WHITE
GRID_COLOR = Color(180, 180, 180)
GEOGRAPHY_COLORS = {
    "land": consts.WHITE,
    "water_area": Color(217, 235, 247),
}
TEX_COLORS = {
    "station": {
        "main": consts.BLACK,
        "sub": Color(140, 140, 140),
        "shadow": consts.WHITE,
    },
    "district": Color(120, 120, 120),
    "water_area": Color(93, 188, 218),
}
METRO_LOGO_COLOR = Color(215, 5, 8)

# svg paths
METRO_LOGO_INFO = {
    "svg_dir": METRO_LOGO_DIR,
    "scale_factor": 15.0,
    "color": METRO_LOGO_COLOR,
    "aligned_point": np_float(20, 380),
}

# styles
GRID_STYLE = {
    "step": 50.0,
    "stroke_width": 0.3,
    "stroke_opacity": 0.15,
    "color": GRID_COLOR,
}
ROUTE_STYLE = {
    "arc_radius": 2.0,
    "stroke_width": 0.8,
    "minor_stroke_width": 0.3,
    "stroke_opacity": 0.7,
}
STATION_POINT_STYLE = {
    "radius": 0.4,
    "fill_opacity": 1.0,
}
STATION_FRAME_STYLE = {
    "radius": {
        "normal": 0.4,
        "interchange": 0.55,
    },
    "stroke_width": {
        "normal": 0.2,
        "interchange": 0.1,
    },
    "stroke_color": {
        "normal": None,
        "interchange": consts.BLACK,
    },
    "stroke_opacity": 0.9,
    "fill_color": consts.WHITE,
    "fill_opacity": 1.0,
}
STATION_NAME_TEX_STYLE = {
    "small_buff": 0.1,
    "big_buff": 0.3,
    "tex_box_format": consts.VERTICAL,
    "tex_buff": -0.2,
    "languages": {
        consts.CHN: {
            "tex_box_index": 0,
            "scale_factor": 1.4,
            "font_cmd": "youyuan",
            "color": TEX_COLORS["station"]["main"],
        },
        consts.ENG: {
            "tex_box_index": 1,
            "scale_factor": 1.0,
            "font_cmd": "sffamily",
            "color": TEX_COLORS["station"]["sub"],
        },
    },
    "shadow": {
        "color": TEX_COLORS["station"]["shadow"],
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
                "tex_box_index": 0,
                "scale_factor": 2.5,
                "font_cmd": "songti",
                "color": TEX_COLORS["district"],
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_cmd": "rmfamily",
                "color": TEX_COLORS["district"],
            },
        },
    },
    "river_name": {
        "tex_box_format": consts.HORIZONTAL,
        "tex_buff": 1.0,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 2.0,
                "font_cmd": "songti",
                "color": TEX_COLORS["water_area"],
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 2.0,
                "font_cmd": "rmfamily",
                "color": TEX_COLORS["water_area"],
            },
        },
    },
    "lake_name": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 2.2,
                "font_cmd": "songti",
                "color": TEX_COLORS["water_area"],
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_cmd": "rmfamily",
                "color": TEX_COLORS["water_area"],
            },
        },
    },
}
