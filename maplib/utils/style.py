from maplib.tools.assertions import assert_is_number
from maplib.tools.simple_functions import modify_num
from maplib.utils.color import Color


class Style(object):
    attr_names = (
        "fill",
        "fill-opacity",
        "mask",
        "stop-color",
        "stop-opacity",
        "stroke",
        "stroke-linecap",
        "stroke-linejoin",
        "stroke-opacity",
        "stroke-width",
    )

    def __init__(self, style_dict):
        self.style_dict = style_dict

    def get_style_xml_str(self):
        partial_strs = []
        for key, val in self.style_dict.items():
            val_str = self.get_val_str(key, val)
            partial_strs.append("{0}:{1}".format(key, val_str))
        return ";".join(partial_strs)

    def get_val_str(self, key, val):
        if key not in self.attr_names:
            raise NotImplementedError(key)
        if key in ("fill", "mask"):
            try:
                return "url(#{0})".format(val.id_name)
            except Exception:
                pass
        if key in ("fill", "stop-color", "stroke"):
            if val is None:
                return "none"
            if isinstance(val, Color):
                return val.hex_str()
        if key in ("fill-opacity", "stop-opacity", "stroke-opacity", "stroke-width"):
            try:
                assert_is_number(val)
                return str(modify_num(val))
            except Exception:
                pass
        if key in ("stroke-linecap", "stroke-linejoin"):
            if isinstance(val, str):
                return val
        raise TypeError

