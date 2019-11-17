from maplib.parameters import SIZE

from maplib.svg.svg_element import Rectangle


class FrameRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name, SIZE)
        self.set_style({
            "stroke-width": 0,
        })

