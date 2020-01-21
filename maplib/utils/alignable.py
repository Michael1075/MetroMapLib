from functools import reduce
from xml.dom import minidom
import numpy as np
import operator as op

import maplib.constants as consts

from maplib.tools.assertions import assert_type
from maplib.tools.numpy_type_tools import np_float
from maplib.tools.space_ops import get_positive_direction
from maplib.utils.params_getter import Container


class Alignable(Container):
    def __init__(self):
        Container.__init__(self)

    def set_box_size(self, box_size):
        self.box_size = box_size
        return self

    def align(self, aligned_point, aligned_direction=consts.ORIGIN):
        self.center_point = aligned_point - self.get_critical_vector(aligned_direction)
        return self

    def align_at_origin(self, aligned_direction=consts.ORIGIN):
        self.align(consts.ORIGIN, aligned_direction)
        return self

    def get_critical_vector(self, direction):
        return self.box_size * direction / 2

    def get_critical_point(self, direction):
        return self.center_point + self.get_critical_vector(direction)


class Frame(Alignable):
    def __init__(self, box_size):
        Alignable.__init__(self)
        self.set_box_size(box_size)


class SvgFrame(Frame):
    def __init__(self, svg_dir):
        doc = minidom.parse(svg_dir)
        box_size = np_float(*[
            doc.getElementsByTagName("svg")[0].getAttribute(attr_name)
            for attr_name in ("width", "height")
        ])
        Frame.__init__(self, box_size)
        doc.unlink()


class Box(Alignable):
    def __init__(self, obj_list, aligned_point, aligned_direction, buff, box_format):
        for obj in obj_list:
            assert_type(obj, Alignable)
        Alignable.__init__(self)
        self.obj_list = obj_list.copy()
        if box_format == consts.VERTICAL:
            obj_list.reverse()
        positive_direction = get_positive_direction(box_format)
        perpendicular_direction = consts.RU - positive_direction
        box_size_list = [obj.box_size for obj in obj_list]
        box_size = reduce(op.add, [
            np.max(box_size_list, axis=0) * perpendicular_direction,
            np.sum(box_size_list, axis=0) * positive_direction,
            (len(obj_list) - 1) * buff * positive_direction
        ])
        self.set_box_size(box_size)
        self.align(aligned_point, aligned_direction)
        partial_aligned_direction = aligned_direction * perpendicular_direction - positive_direction
        major_aligned_point = self.get_critical_point(partial_aligned_direction)
        self.partial_aligned_direction = partial_aligned_direction
        self.partial_aligned_points = [
            reduce(op.add, [
                major_aligned_point,
                np.sum(box_size_list[:k], axis=0) * positive_direction,
                k * buff * positive_direction,
            ])
            for k in range(len(obj_list))
        ]
        if box_format == consts.VERTICAL:
            self.partial_aligned_points.reverse()
