from maplib.constants import *
from maplib.parameters import *

from maplib.svg.svg_element import Group
from maplib.svg.svg_element import Path
from maplib.svg.svg_element import Rectangle
from maplib.tools.position import position
from maplib.utils.alignable import Frame


class FrameRectangle(Rectangle):
    def __init__(self, id_name):
        Rectangle.__init__(self, id_name, SIZE)
        self.set_style({
            "stroke-width": 0,
        })


class BackgroundFrame(Frame):
    def __init__(self):
        Frame.__init__(self, SIZE)
        self.align(ORIGIN, LD)


class Grid(Path):
    def __init__(self, id_name):
        Path.__init__(self, id_name)
        self.set_style({
            "stroke": GRID_COLOR,
            "stroke-opacity": GRID_STROKE_OPACITY,
            "stroke-width": ROUTE_STROKE_WIDTH,
        })
        for k in range(*[round(val) for val in (GRID_STEP, WIDTH, GRID_STEP)]):
            self.move_to(position(k, 0))
            self.line_to(position(k, HEIGHT))
        for k in range(*[round(val) for val in (GRID_STEP, HEIGHT, GRID_STEP)]):
            self.move_to(position(0, k))
            self.line_to(position(WIDTH, k))
        self.finish_path()


class ShanghaiMetroLogo(Group, Frame):
    def __init__(self, id_name):
        Group.__init__(self, id_name)
        scale_factor = METRO_LOGO_SIZE
        Frame.__init__(self, RU * scale_factor)
        self.align(METRO_LOGO_ALIGNED_POINT)
        shift_vector = self.get_critical_point(LD)
        self.scale(scale_factor, shift_vector)
        self.set_style({
            "fill": METRO_LOGO_COLOR,
        })
        path = self.get_path()
        self.append(path)

    def get_path(self):
        path = Path(None)
        path.move_to(position(0.982589, 0.630347))
        path.arc_to(position(0.010749, 0.398316), 0.5, 0, 1)
        path.h_line_to(0.25455)
        path.line_to(position(0.38906, 0.541234))
        path.line_to(position(0.513483, 0.389909))
        path.line_to(position(0.647994, 0.541234))
        path.line_to(position(0.777460, 0.410086))
        path.h_line_to(0.858167)
        path.arc_to(position(0.194019, 0.29407), 0.37313, 0, 0)
        path.h_line_to(0.044376)
        path.arc_to(position(0.999403, 0.52442), 0.5, 0, 1)
        path.h_line_to(0.790912)
        path.line_to(position(0.647994, 0.687514))
        path.line_to(position(0.505076, 0.539552))
        path.line_to(position(0.389060, 0.687514))
        path.line_to(position(0.232192, 0.510969))
        path.h_line_to(0.128446)
        path.arc_to(position(0.853123, 0.630347), 0.37313, 0, 0)
        path.close_path()
        path.finish_path()
        return path

