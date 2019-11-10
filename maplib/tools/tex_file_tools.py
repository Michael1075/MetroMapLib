import os

from maplib.parameters import TEX_FONT_CMDS_CHN
from maplib.parameters import TEX_FONT_CMDS_ENG

from maplib.svg.tex import PureTex


def add_tex(string, font_types, remove_file = False):
    for font_type in font_types:
        pure_tex_obj = PureTex(string, font_type)
        file_name = pure_tex_obj.file_name_body + ".svg"
        print(pure_tex_obj.font_type, file_name)
        if not remove_file:
            pure_tex_obj.tex_to_svg_file()
        else:
            if os.path.exists(file_name):
                os.remove(file_name)
                os.remove(file_name.replace(".svg", ".tex"))


def add_chn_tex(string, remove_file = False):
    add_tex(string, TEX_FONT_CMDS_CHN, remove_file)


def add_eng_tex(string, remove_file = False):
    add_tex(string, TEX_FONT_CMDS_ENG, remove_file)


def remove_chn_tex(string):
    add_chn_tex(string, remove_file = True)


def remove_eng_tex(string):
    add_eng_tex(string, remove_file = True)

