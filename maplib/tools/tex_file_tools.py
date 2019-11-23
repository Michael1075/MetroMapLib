import concurrent.futures as ft
import os

from maplib.parameters import TEX_FONT_CMDS_CHN
from maplib.parameters import TEX_FONT_CMDS_ENG

from maplib.svg.tex import PureTex


def add_single_tex(string, font_type, remove_file = False):
    pure_tex_obj = PureTex(string, font_type)
    file_name = pure_tex_obj.file_name_body + ".svg"
    msg = [os.path.basename(pure_tex_obj.file_name_body), pure_tex_obj.tex_string]
    if not remove_file:
        msg.insert(0, "Creating")
        print(" ".join(msg))
        pure_tex_obj.tex_to_svg_file()
    else:
        msg.insert(0, "Removing")
        print(" ".join(msg))
        if os.path.exists(file_name):
            os.remove(file_name)
            os.remove(file_name.replace(".svg", ".tex"))


def add_tex(string, font_types, remove_file = False):
    with ft.ThreadPoolExecutor() as executor:
        executor.map(lambda font_type: add_single_tex(string, font_type, remove_file), font_types)


def add_chn_tex(string, remove_file = False):
    add_tex(string, TEX_FONT_CMDS_CHN, remove_file)


def add_eng_tex(string, remove_file = False):
    add_tex(string, TEX_FONT_CMDS_ENG, remove_file)


def remove_chn_tex(string):
    add_chn_tex(string, remove_file = True)


def remove_eng_tex(string):
    add_eng_tex(string, remove_file = True)

