from maplib.parameters import *

from maplib.svg.svg_element import Group
from maplib.svg.tex import Tex
from maplib.svg.tex import TexBox
from maplib.svg.tex import TexGroup
from maplib.tools.space_ops import get_simplified_direction


class StationNameBody(TexGroup):
    def __init__(self, id_name, station_objs):
        self.station_objs = station_objs
        partial_groups = self.get_partial_groups()
        TexGroup.__init__(self, id_name, partial_groups)
        self.add_station_name()

    def get_partial_groups(self):
        chn_group = Group("station_name_chn")
        chn_group.scale(LABEL_TEX_CHN_SCALE_FACTOR)
        chn_group.set_style({
            "fill": LABEL_CHN_COLOR,
        })
        eng_group = Group("station_name_eng")
        eng_group.scale(LABEL_TEX_ENG_SCALE_FACTOR)
        eng_group.set_style({
            "fill": LABEL_ENG_COLOR,
        })
        return (chn_group, eng_group)

    def build_tex_objs(self, station):
        # This process writes tex_file and really takes long
        tex_chn_obj = Tex(station.station_name_chn, LABEL_TEX_CHN_FONT_CMD, LABEL_TEX_CHN_SCALE_FACTOR)
        tex_eng_obj = Tex(station.station_name_eng, LABEL_TEX_ENG_FONT_CMD, LABEL_TEX_ENG_SCALE_FACTOR)
        return (tex_chn_obj, tex_eng_obj)

    def add_station_name(self):
        tex_objs_list = [self.build_tex_objs(station) for station in self.station_objs]
        align_buffs = (LABEL_BUFF_BIG, LABEL_BUFF_SMALL)
        line_buff = LABEL_BUFF_BETWEEN_LINES
        for station, tex_objs in zip(self.station_objs, tex_objs_list):
            aligned_direction = station.aligned_direction
            align_buff = align_buffs[get_simplified_direction(aligned_direction) % 2]
            aligned_point = station.aligned_point - aligned_direction * align_buff
            tex_box = TexBox(tex_objs, aligned_point, aligned_direction, line_buff)
            self.append_tex_box(tex_box)
        return self


class StationName(Group):
    def __init__(self, id_name, station_objs):
        self.station_objs = station_objs
        Group.__init__(self, id_name)
        self.flip_y_for_tex()
        self.add_shadow_tex()
        self.add_body_tex()

    def add_shadow_tex(self):
        shadow_group = Group("station_name_shadow")
        shadow_group.set_style({
            "fill": None,
            "stroke": LABEL_SHADOW_COLOR,
            "stroke-width": LABEL_SHADOW_STROKE_WIDTH * 2 / TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": LABEL_SHADOW_OPACITY,
        })
        shadow_group.use("station_name_body")
        self.append(shadow_group)
        return self

    def add_body_tex(self):
        station_name_body = StationNameBody("station_name_body", self.station_objs)
        self.append(station_name_body)
        self.tex_paths_dict = station_name_body.tex_paths_dict
        return self

