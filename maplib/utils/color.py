class Color(object):
    def __init__(self, *rgb):
        if any([val not in range(256) for val in rgb]):
            raise ValueError(rgb)
        self.rgb = rgb

    def __eq__(self, obj):
        return isinstance(obj, Color) and self.rgb == obj.rgb

    def xml_str(self):
        rgb_str = [str(val) for val in self.rgb]
        return "rgb({0})".format(",".join(rgb_str))

    def hex_str(self):
        def get_partial_str(num):
            string = hex(num)[2:].upper()
            if num < 16:
                string = "0" + string
            return string
        return "#" + "".join([get_partial_str(val) for val in self.rgb])

    def simple_str(self, separator=" "):
        return separator.join([str(val) for val in self.rgb])
