from maplib.constants import ORIGIN


class Alignable(object):
    def set_box_size(self, box_size):
        self.box_size = box_size
        return self

    def align(self, aligned_point, aligned_direction = ORIGIN):
        self.center_point = aligned_point - self.get_critical_vector(aligned_direction)
        return self

    def align_at_origin(self, aligned_direction = ORIGIN):
        self.align(ORIGIN, aligned_direction)
        return self

    def get_critical_vector(self, direction):
        return self.box_size * direction / 2

    def get_critical_point(self, direction):
        return self.center_point + self.get_critical_vector(direction)


class Frame(Alignable):
    def __init__(self, box_size):
        self.set_box_size(box_size)

