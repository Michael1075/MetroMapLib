import concurrent.futures as ft

import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.svg_element import Group
from maplib.svg.tex import Tex
from maplib.svg.tex import TexBox
from maplib.svg.tex import TexGroup
from maplib.tools.config_ops import digest_locals
from maplib.tools.space_ops import get_simplified_direction
from maplib.utils.color import Color


class TexNameTemplate(Group):
    body_group_id_name = None

    def __init__(self, id_name, objs, tex_style):
        digest_locals(self)
        Group.__init__(self, id_name)
        self.flip_y()
        if "shadow" in self.tex_style.keys():
            self.add_shadow_tex()
        self.add_body_tex()

    def get_aligning_information(self, obj):
        aligned_point = obj.center_point
        aligned_direction = consts.ORIGIN
        return (aligned_point, aligned_direction)

    def get_partial_groups(self):
        chn_group = Group(None)
        eng_group = Group(None)
        color = self.tex_style["color"]
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
        color = self.tex_style["color"]
        if isinstance(color, Color):
            tex_group.set_style({
                "fill": color,
            })
        return tex_group

    def build_tex_objs(self, obj):
        tex_str_dict = self.get_tex_str_dict(obj)
        return [
            Tex(
                tex_str_dict[language],
                self.tex_style["font_cmd"][language],
                self.tex_style["scale_factor"][language]
            )
            for language in ("chn", "eng")
            if tex_str_dict[language] is not None
        ]

    def get_tex_str_dict(self, obj):
        return {
            "chn": obj.name_chn,
            "eng": obj.name_eng,
        }

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        with ft.ThreadPoolExecutor() as executor:
            tex_objs_list = list(executor.map(self.build_tex_objs, self.objs))
        self.tex_objs = [tex_obj for tex_objs in tex_objs_list for tex_obj in tex_objs]
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        for obj, tex_objs in zip(self.objs, tex_objs_list):
            aligned_point, aligned_direction = self.get_aligning_information(obj)
            tex_box = TexBox(tex_objs, aligned_point, aligned_direction, buff, box_format)
            tex_group.append_tex_box(tex_box)
        self.append(tex_group)
        return self

    def add_shadow_tex(self):
        shadow_style = self.tex_style["shadow"]
        shadow_group = Group(None)
        shadow_group.set_style({
            "fill": None,
            "stroke": shadow_style["color"],
            "stroke-width": shadow_style["stroke_width"] * 2 / params.TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": shadow_style["opacity"],
        })
        shadow_group.use(self.body_group_id_name)
        self.append(shadow_group)
        return self


class StationName(TexNameTemplate):
    body_group_id_name = "station_name_body"

    def __init__(self, id_name, objs):
        TexNameTemplate.__init__(self, id_name, objs, params.STATION_NAME_TEX_STYLE)

    def get_aligning_information(self, station):
        align_buffs = [self.tex_style[key] for key in ("big_buff", "small_buff")]
        label_direction = station.label_direction
        aligned_direction = -label_direction
        align_buff = align_buffs[get_simplified_direction(label_direction) % 2]
        aligned_point = station.frame.get_critical_point(label_direction) + align_buff * label_direction
        return (aligned_point, aligned_direction)


class GeographicName(Group):
    def __init__(self, id_name, name_objs_dict):
        Group.__init__(self, id_name)
        for name_type, obj_list in name_objs_dict.items():
            name_group = TexNameTemplate(name_type, obj_list, params.GEOGRAPHIC_NAME_TEX_STYLE[name_type])
            self.append(name_group)


