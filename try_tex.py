from parameters import *

from tools.tex_file_writing import tex_to_svg_file


if __name__ == "__main__":
    #flush_cmd = "flushleft"
    for font_cmds in (("rmfamily",), ("sffamily",)):
        expression = "{{{0} {1}}}".format(
            " ".join([("\\" + cmd) for cmd in font_cmds]),
            "Zhenbei Road'"
        )
        result = tex_to_svg_file(expression, "_".join(font_cmds))
        print(font_cmds, result)
    for font_cmds in (("heiti",),):
        expression = "{{{0} {1}}}".format(
            " ".join([("\\" + cmd) for cmd in font_cmds]),
            "大木桥路"
        )
        result = tex_to_svg_file(expression, "_".join(font_cmds))
        print(font_cmds, result)

