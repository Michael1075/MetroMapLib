import numpy as np

from maplib.svg.svg_element import Path
from maplib.tools.assertions import assert_is_standard_route
from maplib.tools.config_ops import digest_locals
from maplib.tools.simple_functions import adjacent_n_tuples
from maplib.tools.space_ops import abs_arg_pair
from maplib.tools.space_ops import arg
from maplib.tools.space_ops import get_angle


class CommandPath(Path):
    def __init__(self, id_name, command_str):
        Path.__init__(self, id_name)
        self.add_raw_command(command_str)
        self.finish_path()


class LineArcPath(Path):
    def __init__(self, id_name, control_points, arc_radius, loop):
        digest_locals(self)
        assert_is_standard_route(control_points, loop)
        Path.__init__(self, id_name)
        self.num_arcs = len(control_points)
        if not self.loop:
            self.num_arcs -= 2
        self.create_path()

    def create_path(self):
        before_arc_points = []
        after_arc_points = []
        sweep_flags = []
        for a, b, c in adjacent_n_tuples(self.control_points, 3, self.loop):
            theta = get_angle(a, b, c)
            sweep_flag = 0 if theta >= 0 else 1
            cut_off_length = self.arc_radius / np.tan(abs(theta) / 2)
            h1, h2 = [
                (b + abs_arg_pair(cut_off_length, arg(p - b)))
                for p in [a, c]
            ]
            before_arc_points.append(h1)
            after_arc_points.append(h2)
            sweep_flags.append(sweep_flag)
        if not self.loop:
            before_arc_points.append(self.control_points[-1])
            after_arc_points.append(self.control_points[0])

        self.move_to(after_arc_points[-1])
        for k in range(self.num_arcs):
            self.line_to(before_arc_points[k])
            self.arc_to(after_arc_points[k], self.arc_radius, 0, sweep_flags[k])
        if self.loop:
            self.close_path()
        else:
            self.line_to(before_arc_points[-1])
        self.finish_path()
        return self


class LPath(LineArcPath):
    def __init__(self, id_name, control_points, arc_radius):
        LineArcPath.__init__(self, id_name, control_points, arc_radius, False)


class OPath(LineArcPath):
    def __init__(self, id_name, control_points, arc_radius):
        LineArcPath.__init__(self, id_name, control_points, arc_radius, True)


class YPath(LineArcPath):
    def __init__(self, id_name, main_control_points, sub_control_points, arc_radius):
        LineArcPath.__init__(self, id_name, main_control_points, arc_radius, False)
        sub_path = LineArcPath(None, sub_control_points, arc_radius, False)
        self.add_element_path(sub_path)

