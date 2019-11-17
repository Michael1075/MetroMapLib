from maplib.constants import ORIGIN


class Alignable(object):
    def set_box_size(self, box_size):
        self.semi_box_size = box_size / 2
        return self

    def align(self, aligned_point, aligned_direction = ORIGIN):
        self.center_point = aligned_point - aligned_direction * self.semi_box_size
        return self

    def get_critical_vector(self, direction):
        return self.semi_box_size * direction

    def get_critical_point(self, direction):
        return self.center_point + self.get_critical_vector(direction)

    def align_at_origin(self, aligned_direction = ORIGIN):
        self.align(ORIGIN, aligned_direction)
        return self

