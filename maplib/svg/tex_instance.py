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
        self.set_sorted_languages()
        Group.__init__(self, id_name)
        self.flip_y()
        if "shadow" in self.tex_style.keys():
            self.add_shadow_tex()
        self.add_body_tex()

    def get_aligning_information(self, obj):
        aligned_point = obj.center_point
        aligned_direction = consts.ORIGIN
        return (aligned_point, aligned_direction)

    def set_sorted_languages(self):
        language_list = []
        for language, language_style in self.tex_style["languages"].items():
            if language_style["exists"]:
                language_index = language_style["tex_box_index"]
                language_list.append((language_index, language))
        language_list.sort(key = lambda pair: pair[0])
        self.sorted_languages = tuple([pair[1] for pair in language_list])
        return self

    def get_language_style(self, language):
        return self.tex_style["languages"][language]

    def get_partial_groups(self):
        group_list = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            partial_group = Group(None)
            partial_group.set_style({
                "fill": language_style["color"],
            })
            group_list.append(partial_group)
        return group_list

    def get_tex_group(self):
        partial_groups = self.get_partial_groups()
        tex_group = TexGroup(self.body_group_id_name, partial_groups)
        return tex_group

    def build_tex_objs(self, obj):
        tex_str_dict = obj.get_name_dict()
        tex_objs = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            tex_obj = Tex(
                tex_str_dict[language],
                language_style["font_cmd"],
                language_style["scale_factor"]
            )
            tex_objs.append(tex_obj)
        return tex_objs

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


