import hashlib
import os
import re

from maplib.parameters import *


def tex_hash(string):
    hasher = hashlib.sha256()
    hasher.update(string.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16].upper()


def filter_out_string(new_body):
    re_str = r"(?<=\\begin\{document\})\n(.*)\n(?=\\end\{document\})"
    string = re.search(re_str, new_body).group(1)
    return string


def generate_tex_file(new_body, file_name):
    result = file_name.replace(".svg", ".tex")
    if PRINT_TEX_WRITING_PROGRESS:
        print("Writing \"{0}\" to {1}".format(filter_out_string(new_body), file_name))
    with open(result, "w", encoding = "utf-8") as outfile:
        outfile.write(new_body)
    return result


def tex_to_dvi(tex_file):
    result = tex_file.replace(".tex", ".xdv")
    file_dir = os.path.dirname(tex_file)
    commands = [
        "xelatex",
        "-no-pdf",
        "-interaction=batchmode",
        "-halt-on-error",
        "-output-directory=" + file_dir,
        tex_file,
        ">",
        os.devnull
    ]
    exit_code = os.system(" ".join(commands))
    if exit_code != 0:
        raise OSError
    return result


def dvi_to_svg(dvi_file):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".xdv", ".svg")
    commands = [
        "dvisvgm",
        dvi_file,
        "-n",
        "-v",
        "0",
        "-o",
        result,
        ">",
        os.devnull
    ]
    os.system(" ".join(commands))
    return result


def tex_to_svg(new_body, file_name_body):
    svg_file_name = file_name_body + ".svg"
    if os.path.exists(svg_file_name):
        return svg_file_name
    file_dir = os.path.dirname(svg_file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    tex_file = generate_tex_file(new_body, svg_file_name)
    dvi_file = tex_to_dvi(tex_file)
    svg_file = dvi_to_svg(dvi_file)
    os.remove(file_name_body + ".xdv")
    os.remove(file_name_body + ".log")
    os.remove(file_name_body + ".aux")
    return svg_file

