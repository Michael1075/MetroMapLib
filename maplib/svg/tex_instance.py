import concurrent.futures as ft

from maplib.constants import ORIGIN
from maplib.parameters import *

from maplib.svg.svg_element import Group
from maplib.svg.tex import Tex
from maplib.svg.tex import TexBox
from maplib.svg.tex import TexGroup
from maplib.tools.space_ops import get_simplified_direction


class TexNameTemplate(Group):
    def __init__(self, id_name, objs):
        Group.__init__(self, id_name)
        self.flip_y_for_tex()
        self.objs = objs
        if "shadow" in self.tex_style.keys():
            self.add_shadow_tex()
        self.add_body_tex()

    def get_partial_groups(self):
        chn_group = Group(None)
        eng_group = Group(None)
        scale_factor = self.tex_style["scale_factor"]
        color = self.tex_style["color"]
        if isinstance(scale_factor, dict):
            chn_group.scale(scale_factor["chn"])
            eng_group.scale(scale_factor["eng"])
        if isinstance(color, dict):
            chn_group.set_style({
                "fill": color["chn"],
            })
            eng_group.set_style({
                "fill": color["eng"],
            })
        return (chn_group, eng_group)

    def get_tex_group(self):
        partial_groups = self.get_partial_groups()
        tex_group = TexGroup(self.body_group_id_name, partial_groups)
        scale_factor = self.tex_style["scale_factor"]
        color = self.tex_style["color"]
        if not isinstance(scale_factor, dict):
            tex_group.scale(scale_factor)
        if not isinstance(color, dict):
            tex_group.set_style({
                "fill": color,
            })
        return tex_group

    def build_tex_objs(self, obj):
        tex_strs = self.get_tex_strs(obj)
        return tuple([
            Tex(tex_strs[language], self.tex_style["font_cmd"][language], self.tex_style["scale_factor"][language])
            for language in ("chn", "eng")
            if tex_strs[language]
        ])

    def get_tex_strs(self, obj):
        return {
            "chn": obj.name_chn,
            "eng": obj.name_eng,
        }

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        with ft.ThreadPoolExecutor() as executor:
            tex_objs_list = list(executor.map(self.build_tex_objs, self.objs))
        line_buff = self.tex_style["buff_between_lines"]
        for obj, tex_objs in zip(self.objs, tex_objs_list):
            aligned_point, aligned_direction = self.get_aligning_information(obj)
            tex_box = TexBox(tex_objs, aligned_point, aligned_direction, line_buff)
            tex_group.append_tex_box(tex_box)
        self.append(tex_group)
        self.tex_paths_dict = tex_group.tex_paths_dict
        return self

    def add_shadow_tex(self):
        shadow_style = self.tex_style["shadow"]
        shadow_group = Group(None)
        shadow_group.set_style({
            "fill": None,
            "stroke": shadow_style["color"],
            "stroke-width": shadow_style["stroke_width"] * 2 / TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": shadow_style["opacity"],
        })
        shadow_group.use(self.body_group_id_name)
        self.append(shadow_group)
        return self


class StationName(TexNameTemplate):
    tex_style = STATION_NAME_TEX_STYLE
    body_group_id_name = "station_name_body"

    def get_aligning_information(self, station):
        align_buffs = [self.tex_style[key] for key in ("big_buff", "small_buff")]
        label_direction = station.label_direction
        aligned_direction = -label_direction
        align_buff = align_buffs[get_simplified_direction(label_direction) % 2]
        aligned_point = station.frame.get_critical_point(label_direction) + align_buff * label_direction
        return (aligned_point, aligned_direction)


class DistrictName(TexNameTemplate):
    tex_style = DISTRICT_NAME_TEX_STYLE
    body_group_id_name = "district_name_body"

    def get_aligning_information(self, district_name):
        aligned_point = district_name.center_point
        aligned_direction = ORIGIN
        return (aligned_point, aligned_direction)


class WaterAreaName(TexNameTemplate):
    tex_style = WATER_AREA_NAME_TEX_STYLE
    body_group_id_name = "water_area_name_body"

    def get_aligning_information(self, water_area_name):
        aligned_point = water_area_name.center_point
        aligned_direction = ORIGIN
        return (aligned_point, aligned_direction)

