import concurrent.futures as ft

import maplib.constants as consts

from maplib.svg.misc import NumberNameFrame
from maplib.svg.misc import StringsNameFrame
from maplib.svg.misc import SvgPathTemplate
from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Path
from maplib.svg.tex import Tex
from maplib.svg.tex import TexFileWriter
from maplib.svg.tex import TexGroup
from maplib.tools.json_file_tools import JsonTools
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.simple_functions import remove_list_redundancies
from maplib.tools.space_ops import get_simplified_direction
from maplib.utils.alignable import Box
from maplib.utils.models import AuthorItem
from maplib.utils.models import CopyrightInfo
from maplib.utils.models import MetroName
from maplib.utils.models import Title
from maplib.utils.params_getter import Container


class TexNameTemplate(Group):
    same_color = True

    def __init__(self, id_name, objs, tex_style):
        self.objs = objs
        self.tex_style = tex_style
        self.has_shadow = "shadow" in self.tex_style.keys()
        self.sorted_languages = self.get_sorted_languages()
        Group.__init__(self, id_name)
        self.flip_y()
        if self.has_shadow:
            self.body_group_id_name = self.id_name + "_body"
            self.add_shadow_tex()
        else:
            self.body_group_id_name = None
        self.add_body_tex()

    def get_aligning_information(self, obj):
        aligned_point = obj.aligned_point
        aligned_direction = obj.aligned_direction
        return aligned_point, aligned_direction

    def get_color(self, language):
        language_style = self.get_language_style(language)
        return language_style["color"]

    def get_special_color(self, language, obj):
        """
        Implemented in subclasses.
        """
        return self.get_color(language)

    def get_sorted_languages(self):
        language_list = []
        for language, language_style in self.tex_style["languages"].items():
            if language_style["tex_box_index"] is not None:
                language_index = language_style["tex_box_index"]
                language_list.append((language_index, language))
        language_list.sort(key = lambda pair: pair[0])
        return tuple([pair[1] for pair in language_list])

    def get_language_style(self, language):
        return self.tex_style["languages"][language]

    def get_partial_groups(self):
        group_list = []
        for language in self.sorted_languages:
            partial_group = Group(None)
            if self.same_color:
                color = self.get_color(language)
                partial_group.set_style({
                    "fill": color,
                })
            group_list.append(partial_group)
        return group_list

    def get_tex_group(self):
        partial_groups = self.get_partial_groups()
        tex_group = TexGroup(self.body_group_id_name, partial_groups)
        return tex_group

    @staticmethod
    def construct_tex(string_and_cmd):
        string, cmd = string_and_cmd
        writer = TexFileWriter(string, cmd)
        writer.write_directly()
        return writer

    def get_tex_obj_list(self, obj, tex_dict_cache):
        tex_obj_list = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            tex_obj = Tex(
                obj.name_dict[language],
                language_style["font_type"],
                language_style["scale_factor"],
                tex_dict_cache
            )
            if not self.same_color:
                color = self.get_special_color(language, obj)
                tex_obj.set_style({
                    "fill": color
                })
            tex_obj_list.append(tex_obj)
        return tex_obj_list

    @staticmethod
    def get_dict_from_tex_cache(tex_cache):
        empty_dict = JsonTools.get_empty_font_type_dict()
        tex_dict_cache = {
            "file": empty_dict,
            "path": empty_dict,
        }
        return JsonTools.generate_tex_in_json(tex_cache, tex_dict_cache)

    def get_tex_dict_cache(self):
        string_and_cmd_list = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            font_type = language_style["font_type"]
            for obj in self.objs:
                tex_str_dict = obj.name_dict
                string = tex_str_dict[language]
                string_and_cmd_list.append((string, font_type))
        filtered_string_and_cmd_list = remove_list_redundancies(string_and_cmd_list)
        with ft.ThreadPoolExecutor() as executor:
            tex_cache = list(executor.map(TexNameTemplate.construct_tex, filtered_string_and_cmd_list))
        tex_dict_cache = TexNameTemplate.get_dict_from_tex_cache(tex_cache)
        return tex_dict_cache

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        tex_dict_cache = self.get_tex_dict_cache()
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        tex_objs = []
        for obj in self.objs:
            tex_obj_list = self.get_tex_obj_list(obj, tex_dict_cache)
            aligned_point, aligned_direction = self.get_aligning_information(obj)
            tex_box = Box(tex_obj_list, aligned_point, aligned_direction, buff, box_format)
            tex_group.append_tex_box(tex_box)
            for tex_obj in tex_obj_list:
                tex_objs.append(tex_obj)
        self.append(tex_group)
        self.tex_objs = tex_objs
        return self

    def add_shadow_tex(self):
        shadow_style = self.tex_style["shadow"]
        shadow_group = Group(None)
        shadow_group.set_style({
            "fill": None,
            "stroke": shadow_style["color"],
            "stroke-width": shadow_style["stroke_width"] * 2 / self.params.TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": shadow_style["opacity"],
        })
        shadow_group.use(self.body_group_id_name)
        self.append(shadow_group)
        return self


class CenterAlignedTexNameTemplate(TexNameTemplate):
    def get_aligning_information(self, obj):
        aligned_point = obj.center_point
        aligned_direction = consts.ORIGIN
        return aligned_point, aligned_direction


class AlignedTexNameTemplate(TexNameTemplate):
    def get_aligning_information(self, obj):
        align_buffs = [self.tex_style[key] for key in ("big_buff", "small_buff")]
        label_direction = obj.label_direction
        aligned_direction = -label_direction
        align_buff = align_buffs[get_simplified_direction(label_direction) % 2]
        aligned_point = obj.frame.get_critical_point(label_direction) + align_buff * label_direction
        return aligned_point, aligned_direction


class ListTexNameTemplate(TexNameTemplate):
    def add_body_tex(self):
        tex_group = self.get_tex_group()
        tex_dict_cache = self.get_tex_dict_cache()
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        item_buff = self.tex_style["item_buff"]
        aligned_point = self.tex_style["aligned_point"]
        aligned_direction = self.tex_style["aligned_direction"]
        simplified_direction = get_simplified_direction(aligned_direction)
        assert simplified_direction % 2 == 0, aligned_direction
        if simplified_direction in (0, -2):
            self.objs.reverse()
        tex_objs = []
        for obj in self.objs:
            tex_obj_list = self.get_tex_obj_list(obj, tex_dict_cache)
            tex_box = Box(tex_obj_list, aligned_point, aligned_direction, buff, box_format)
            tex_group.append_tex_box(tex_box)
            for tex_obj in tex_obj_list:
                tex_objs.append(tex_obj)
            aligned_point -= (tex_box.box_size + item_buff * consts.RU) * aligned_direction
        self.append(tex_group)
        self.tex_objs = tex_objs
        return self


class StationName(AlignedTexNameTemplate):
    def __init__(self, id_name, station_objs):
        Container.__init__(self)
        AlignedTexNameTemplate.__init__(self, id_name, station_objs, self.params.STATION_NAME_TEX_STYLE)


class SingleGeographicName(CenterAlignedTexNameTemplate):
    pass


class GeographicName(Group):
    def __init__(self, id_name, name_objs_dict):
        Group.__init__(self, id_name)
        for name_type, obj_list in name_objs_dict.items():
            name_group = SingleGeographicName(
                name_type + "_group", obj_list, self.params.GEOGRAPHIC_NAME_TEX_STYLE[name_type]
            )
            self.append(name_group)


class SingleSignName(CenterAlignedTexNameTemplate):
    same_color = False

    def __init__(self, id_name, metro_list, tex_style):
        self.metro_list = metro_list
        metro_name_list_dict = self.get_metro_name_list_dict()
        metro_name_objs = []
        for metro_name_list in metro_name_list_dict.values():
            metro_name_objs.extend(metro_name_list)
        self.metro_name_list_dict = metro_name_list_dict
        self.init_template()
        CenterAlignedTexNameTemplate.__init__(self, id_name, metro_name_objs, tex_style)

    def get_special_color(self, language, metro_name_obj):
        return metro_name_obj.color

    def get_metro_name_list_dict(self):
        metro_name_list_dict = {}
        for metro in self.metro_list:
            metro_name_list = []
            for name_coord in metro.names_coord:
                metro_name_obj = MetroName(metro, name_coord)
                metro_name_list.append(metro_name_obj)
            metro_name_list_dict[metro.layer_num] = metro_name_list
        return metro_name_list_dict

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        tex_dict_cache = self.get_tex_dict_cache()
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        tex_objs = []
        tex_box_size_dict = {}
        for metro in self.metro_list:
            for obj in self.metro_name_list_dict[metro.layer_num]:
                tex_obj_list = self.get_tex_obj_list(obj, tex_dict_cache)
                aligned_point, aligned_direction = self.get_aligning_information(obj)
                tex_box = Box(tex_obj_list, aligned_point, aligned_direction, buff, box_format)
                tex_group.append_tex_box(tex_box)
                tex_box_size_dict[metro.layer_num] = tex_box.box_size
                for tex_obj in tex_obj_list:
                    tex_objs.append(tex_obj)
        self.append(tex_group)
        self.tex_objs = tex_objs
        self.tex_box_size_dict = tex_box_size_dict
        return self


class SignName(Group):
    def __init__(self, id_name, metro_objs):
        Group.__init__(self, id_name)
        self.init_template()
        type_to_metros_dict = {
            "number": [],
            "strings": [],
        }
        for metro in metro_objs:
            name_type = metro.get_name_type()
            type_to_metros_dict[name_type].append(metro)
        for name_type, metro_list in type_to_metros_dict.items():
            name_group = self.get_name_group(name_type, metro_list)
            frame_group = self.get_frame_group(name_type, metro_list, name_group)
            self.append(frame_group)
            self.append(name_group)

    def get_name_group(self, name_type, metro_list):
        return SingleSignName(name_type, metro_list, self.params.SIGN_TEX_STYLE[name_type])

    def get_frame_group(self, name_type, metro_list, name_group):
        frame_group = Group(None)
        frame_group.set_style({
            "fill-opacity": self.params.SIGN_NAME_STYLE["fill_opacity"],
        })
        for metro in metro_list:
            if name_type == "number":
                frame_template = NumberNameFrame(metro)
            elif name_type == "strings":
                box_size = name_group.tex_box_size_dict[metro.layer_num]
                frame_template = StringsNameFrame(metro, box_size)
            else:
                raise NotImplementedError(name_type)
            self.template.append(frame_template)
            for coord in metro.names_coord:
                frame_group.use(metro.sign_id_name, coord)
        return frame_group


class SingleMarkGroup(AlignedTexNameTemplate):
    pass


class MarkGroup(Group):
    def __init__(self, id_name, mark_objs_dict):
        Group.__init__(self, id_name)
        self.init_template()
        for mark_type, obj_list in mark_objs_dict.items():
            logo_style = self.params.MARK_LOGO_STYLE[mark_type]
            logo_template = SvgPathTemplate(
                mark_type, logo_style["scale_factor"], consts.LOGO_DIRS[mark_type]
            )
            self.template.append(logo_template)
            for obj in obj_list:
                self.use_with_style(mark_type, {
                    "fill": logo_style["color"],
                }, obj.center_point)
            mark_group = SingleMarkGroup(
                mark_type + "_group", obj_list, self.params.MARK_TEX_STYLE[mark_type]
            )
            self.append(mark_group)


class TitleGroup(TexNameTemplate):
    def __init__(self, id_name):
        Container.__init__(self)
        title_obj = Title(self.params.INFO_STRINGS["title"])
        TexNameTemplate.__init__(self, id_name, [title_obj], self.params.INFO_TEX_STYLE["title"])


class AuthorCatalogueGroup(ListTexNameTemplate):
    def __init__(self, id_name):
        Container.__init__(self)
        key_names = self.params.INFO_STRINGS["author"]
        author_items = [
            AuthorItem(key_names["project_author"], self.params.PROJECT_AUTHOR),
            AuthorItem(key_names["code_author"], consts.CODE_AUTHOR),
            AuthorItem(key_names["github_url"], consts.GITHUB_URL),
        ]
        ListTexNameTemplate.__init__(self, id_name, author_items, self.params.INFO_TEX_STYLE["author"])


class CopyrightGroup(ListTexNameTemplate):
    def __init__(self, id_name):
        Container.__init__(self)
        copyright_objs = [
            CopyrightInfo(info) for info in self.params.INFO_STRINGS["copyright"]
        ]
        ListTexNameTemplate.__init__(
            self, id_name, copyright_objs, self.params.INFO_TEX_STYLE["copyright"]
        )


class MapInfo(Group):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        separator = self.get_separator()
        metro_logo = self.get_metro_logo()
        tex_components = self.get_tex_components()
        self.append(separator)
        self.append(metro_logo)
        for component in tex_components:
            self.append(component)

    def get_separator(self):
        separator = Path(None)
        height = self.params.SEPARATOR_STYLE["height"]
        begin_x = self.params.SEPARATOR_STYLE["buff"]
        end_x = self.params.FULL_WIDTH - begin_x
        separator.move_to(np_float(begin_x, height))
        separator.h_line_to(end_x)
        separator.finish_path()
        separator.set_style({
            "stroke": self.params.SEPARATOR_STYLE["color"],
            "stroke-width": self.params.SEPARATOR_STYLE["stroke_width"],
        })
        return separator

    def get_metro_logo(self):
        metro_logo_group = Group(None)
        metro_logo_style = self.params.METRO_LOGO_STYLE
        metro_logo = SvgPathTemplate(None, metro_logo_style["scale_factor"], self.params.METRO_LOGO_DIR)
        
        metro_logo.set_style({
            "fill": metro_logo_style["color"],
        })
        metro_logo_group.append(metro_logo)
        metro_logo_group.shift(metro_logo_style["aligned_point"])
        return metro_logo_group

    def get_tex_components(self):
        return (
            TitleGroup("title"),
            AuthorCatalogueGroup("author"),
            CopyrightGroup("copyright"),
        )
