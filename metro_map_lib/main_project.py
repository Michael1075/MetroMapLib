import time

from constructor import metro_objs
from constructor import station_objs

from drawing import Drawing
from drawing import main


class Ex(Drawing):
    def construct(self):
        self.add(*metro_objs, *station_objs)
        

if __name__ == "__main__":
    main(Ex, r"files\pdf1.pdf", 400, 300, open_at_once = True)
