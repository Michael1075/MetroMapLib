import cairo
import numpy as np
import os
import time

from mobject.mobject import Mobject

from tools.simple_functions import unit_to_point


class Drawing(object):
    def __init__(self, check_components = False):
        self.components = []
        self.construct()
        self.sort_components_by_layers()
        if check_components:
            self.check_components()

    def construct(self):
        pass

    def add(self, *objs):
        for obj in objs:
            assert isinstance(obj, Mobject)
            if hasattr(obj, "components"):
                self.add(*obj.components)
            else:
                self.components.append(obj)
        return self

    def sort_components_by_layers(self):
        self.components.sort(key = lambda component: component.layer)

    def check_components(self):
        for component in self.components:
            print(component, component.layer)


def create_PDF_context(file_name, width, height):
    surface = cairo.PDFSurface(
        file_name,
        unit_to_point(width),
        unit_to_point(height)
    )
    ctx = cairo.Context(surface)
    size = (width, height)
    return surface, ctx, size


def main(DrawingClass, file_name, width, height, open_at_once = True, test_time = False):
    if test_time:
        begin = time.time()
    surface, ctx, size = create_PDF_context(file_name, width, height)
    drawing = DrawingClass()
    for component in drawing.components:
        ctx = component.on_draw(ctx, size)
    ctx.show_page()
    surface.finish()
    if test_time:
        end = time.time()
        print("Elapsed time: %.3f second(s)" % (end - begin))
    if open_at_once:
        os.system(file_name)

