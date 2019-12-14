class Color(object):
    def __init__(self, *rgb):
        assert all([val in range(256) for val in rgb]), ValueError(rgb)
        self.rgb = rgb

    def __eq__(self, obj):
        return isinstance(obj, Color) and self.rgb == obj.rgb

    def get_color_xml_str(self):
        rgb_str = [str(val) for val in self.rgb]
        return "rgb({0})".format(",".join(rgb_str))

    def hex_str(self):
        def get_partial_str(num):
            string = hex(num)[2:].upper()
            if num < 16:
                string = "0" + string
            return string
        return "#" + "".join([get_partial_str(val) for val in self.rgb])
        
