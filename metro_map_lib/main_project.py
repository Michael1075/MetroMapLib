from drawing import Drawing
from drawing import main

from mobject.constructor import metro_objs
from mobject.constructor import station_objs


class Project(Drawing):
    def construct(self):
    	#svg_file = SVGMobject("files\\tex\\svg_sample1.svg")
        self.add(*metro_objs, *station_objs)
        

if __name__ == "__main__":
    main(Project, "files\\output_file\\pdf1.pdf", 400, 300, open_at_once = True)
    #main(Project, "files\\output_file\\svg1.svg", 400, 300, open_at_once = True)
