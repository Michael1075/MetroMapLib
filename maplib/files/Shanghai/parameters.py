import maplib.constants as consts

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


# project author
PROJECT_AUTHOR = "Michael W"

# svg base
SVG_VERSION = "1.1"
SVG_XMLNS = "http://www.w3.org/2000/svg"
SVG_XLINK = "http://www.w3.org/1999/xlink"

# size
FULL_WIDTH = 460.0
FULL_HEIGHT = 360.0
BODY_WIDTH = 450.0
BODY_HEIGHT = 320.0

# composition
MAP_GROUP_SHIFT_VECTOR = np_float(5.0, 40.0)
MAP_BODY_SHIFT_VECTOR = np_float(20.0, 0.0)
GRADIENT_WIDTH = 20.0
GRADIENT_HEIGHT = 20.0

# mask
MASK_BASE_COLOR = consts.WHITE
MASK_COLOR = consts.BLACK

# tex
TEX_BASE_SCALE_FACTOR = 0.07

# strings
INFO_STRINGS = {
    "title": {
        consts.CHN: "上海轨道交通网络示意图",
        consts.ENG: "SHANGHAI METRO NETWORK MAP",
    },
    "author": {
        "project_author": "设计",
        "code_author": "代码",
        "github_url": "源",
    },
    "copyright": [
        "本图经过变形设计处理，部分规划建设，内容仅供参考。",
        "禁止未经授权的商业用途。",
    ],
}

# colors
MAIN_COLOR = consts.WHITE
GEOGRAPHY_COLORS = {
    "land": consts.WHITE,
    "water_area": Color(217, 235, 247),
}

# styles
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
SIGN_NAME_STYLE = {
    "number_frame_side_length": 3.0,
    "strings_frame_side_buff": 0.4,
    "corner_radius": 0.5,
    "fill_opacity": 0.8,
}
MARK_LOGO_STYLE = {
    "railway_station": {
        "scale_factor": 2.0,
        "color": Color(31, 143, 255),
    },
    "airport": {
        "scale_factor": 2.0,
        "color": Color(126, 101, 159),
    },
}
GRID_STYLE = {
    "step": 50.0,
    "stroke_width": 0.3,
    "stroke_opacity": 0.15,
    "color": Color(180, 180, 180),
}
SEPARATOR_STYLE = {
    "height": 35.0,
    "buff": 5.0,
    "stroke_width": 1.2,
    "color": Color(226, 226, 226),
}
METRO_LOGO_STYLE = {
    "scale_factor": 15.0,
    "color": Color(215, 5, 8),
    "aligned_point": np_float(20.0, 20.0),
}

# tex styles
STATION_NAME_TEX_STYLE = {
    "tex_box_format": consts.VERTICAL,
    "tex_buff": -0.2,
    "small_buff": 0.1,
    "big_buff": 0.3,
    "languages": {
        consts.CHN: {
            "tex_box_index": 0,
            "scale_factor": 1.4,
            "font_type": "youyuan",
            "color": consts.BLACK,
        },
        consts.ENG: {
            "tex_box_index": 1,
            "scale_factor": 1.0,
            "font_type": "sffamily",
            "color": Color(140, 140, 140),
        },
    },
    "shadow": {
        "stroke_width": 0.07,
        "opacity": 0.7,
        "color": consts.WHITE,
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
                "font_type": "songti",
                "color": Color(120, 120, 120),
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_type": "rmfamily",
                "color": Color(120, 120, 120),
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
                "font_type": "songti",
                "color": Color(93, 188, 218),
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 2.0,
                "font_type": "rmfamily",
                "color": Color(93, 188, 218),
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
                "font_type": "songti",
                "color": Color(93, 188, 218),
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_type": "rmfamily",
                "color": Color(93, 188, 218),
            },
        },
    },
}
SIGN_TEX_STYLE = {
    "number": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": 0.0,
        "languages": {
            consts.ENG: {
                "tex_box_index": 0,
                "scale_factor": 3.0,
                "font_type": "sffamily",
            },
        },
    },
    "strings": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.2,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 2.0,
                "font_type": "heiti",
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 1.4,
                "font_type": "sffamily",
            },
        },
    },
}
MARK_TEX_STYLE = {
    "railway_station": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": 0.0,
        "small_buff": 0.1,
        "big_buff": 0.3,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 1.2,
                "font_type": "heiti",
                "color": Color(31, 143, 255),
            },
        },
        "shadow": {
            "stroke_width": 0.07,
            "opacity": 0.7,
            "color": consts.WHITE,
        },
    },
    "airport": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": 0.0,
        "small_buff": 0.1,
        "big_buff": 0.3,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 1.2,
                "font_type": "heiti",
                "color": Color(126, 101, 159),
            },
        },
        "shadow": {
            "stroke_width": 0.07,
            "opacity": 0.7,
            "color": consts.WHITE,
        },
    },
}
INFO_TEX_STYLE = {
    "title": {
        "tex_box_format": consts.VERTICAL,
        "tex_buff": -0.5,
        "aligned_point": np_float(35.0, 20.0),
        "aligned_direction": consts.LEFT,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 11.0,
                "font_type": "heiti",
                "color": Color(124, 145, 211),
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 7.2,
                "font_type": "sffamily",
                "color": Color(181, 193, 230),
            },
        },
    },
    "author": {
        "tex_box_format": consts.HORIZONTAL,
        "tex_buff": 3.0,
        "item_buff": 15.0,
        "aligned_point": np_float(450.0, 25.0),
        "aligned_direction": consts.RIGHT,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 5.0,
                "font_type": "heiti",
                "color": Color(145, 159, 166),
            },
            consts.ENG: {
                "tex_box_index": 1,
                "scale_factor": 5.0,
                "font_type": "sffamily",
                "color": Color(145, 159, 166),
            },
        },
    },
    "copyright": {
        "tex_box_format": consts.HORIZONTAL,
        "tex_buff": 0.0,
        "item_buff": 15.0,
        "aligned_point": np_float(450.0, 16.0),
        "aligned_direction": consts.RIGHT,
        "languages": {
            consts.CHN: {
                "tex_box_index": 0,
                "scale_factor": 5.0,
                "font_type": "heiti",
                "color": Color(145, 159, 166),
            },
        },
    },
}
