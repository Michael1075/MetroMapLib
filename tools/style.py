from tools.assertions import is_number
from tools.color import Color
from tools.simple_functions import modify_num


class Style(object):
    attr_names = (
        "fill",
        "fill-opacity",
        "stroke",
        "stroke-width",
        "stroke-opacity",
        "stroke-linecap",
        "stroke-linejoin",
    )

    def __init__(self, style_dict):
        self.style_dict = style_dict

    def get_style_xml_str(self):
        partial_strs = []
        for key, val in self.style_dict.items():
            if key not in self.attr_names:
                raise NotImplementedError
            if key in ("fill", "stroke"):
                if val is None:
                    val_str = "none"
                elif isinstance(val, Color):
                    val_str = val.hex_str()
                else:
                    raise TypeError
            elif key in ("fill-opacity", "stroke-width", "stroke-opacity"):
                assert is_number(val)
                val_str = str(modify_num(val))
            else:
                val_str = val
            partial_strs.append("{0}:{1}".format(key, val_str))
        return ";".join(partial_strs)

