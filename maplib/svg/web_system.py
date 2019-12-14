import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.svg_element import Group
from maplib.tools.config_ops import digest_locals


class WebSystem(Group):
    def __init__(self, id_name, metro_objs, station_objs):
        digest_locals(self, ("metro_objs", "station_objs"))
        Group.__init__(self, id_name)
        self.init_template_group()
        self.classify_stations()
        self.def_mask_rect()
        self.add_route()
        self.add_normal_station_frame()
        self.add_interchange_station_frame()
        self.add_station_frame()
        self.add_station_point()

    def init_template_group(self):
        self.template_group = Group(None)
        return self

    def classify_stations(self):
        self.normal_stations = []
        self.interchange_stations = []
        for station in self.station_objs:
            if station.is_normal:
                self.normal_stations.append(station)
            else:
                self.interchange_stations.append(station)
        return self

    def def_mask_rect(self):
        mask_rect_group = Group("mask_rect")
        mask_rect_group.use_with_style("frame_rect", {
            "fill": params.MASK_BASE_COLOR,
        })
        self.template_group.append(mask_rect_group)

    def add_route(self):
        route_mask_group = Group("route_mask")
        route_mask_group.set_style({
            "fill": None,
            "stroke-width": params.ROUTE_MINOR_STROKE_WIDTH,
            "stroke": params.MASK_COLOR,
        })
        for metro in self.metro_objs:
            route_path_template = metro.get_route()
            self.template_group.append(route_path_template)
            if metro.sub_color is not None:
                mask_template = metro.get_mask()
                metro.set_mask(mask_template)
                route_mask_group.append(mask_template)
        self.template_group.append(route_mask_group)

        route_group = Group("route")
        route_group.set_style({
            "fill": None,
            "stroke-opacity": params.ROUTE_STROKE_OPACITY,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        main_route_group = Group("main_route")
        main_route_group.set_style({
            "stroke-width": params.ROUTE_STROKE_WIDTH,
        })
        sub_route_group = Group("sub_route")
        sub_route_group.set_style({
            "stroke-width": params.ROUTE_MINOR_STROKE_WIDTH,
        })
        for metro in list(reversed(self.metro_objs)):
            if metro.sub_color is None:
                main_route_group.use_with_style(metro.route_id_name, {
                    "stroke": metro.main_color,
                })
            else:
                main_route_group.use_with_style(metro.route_id_name, {
                    "stroke": metro.main_color,
                    "mask": metro.mask,
                })
                if metro.sub_color != "None":
                    sub_route_group.use_with_style(metro.route_id_name, {
                        "stroke": metro.sub_color,
                    })
        route_group.append(main_route_group)
        route_group.append(sub_route_group)
        self.append(route_group)
        return self

    def add_normal_station_frame(self):
        for metro in self.metro_objs:
            template = metro.get_normal_station_frame()
            self.template_group.append(template)

        normal_station_frame_group = Group("normal_station_frame")
        normal_station_frame_group.set_style({
            "stroke-width": params.FRAME_STROKE_WIDTH_DICT["normal"],
        })
        for station in self.normal_stations:
            normal_station_frame_group.use(station.parent_metro.frame_id_name, station.center_point)
        self.append(normal_station_frame_group)
        return self

    def add_interchange_station_frame(self):
        station_type_set = set()
        template_list = []
        for station in self.interchange_stations:
            if station.station_type not in station_type_set:
                station_type_set.add(station.station_type)
                template = station.get_interchange_station_frame()
                template_list.append(template)
        template_list.sort(key = lambda template: template.id_name)
        for template in template_list:
            self.template_group.append(template)

        interchange_station_frame_group = Group("interchange_station_frame")
        interchange_station_frame_group.set_style({
            "stroke": params.INTERCHANGE_STATION_FRAME_STROKE_COLOR,
            "stroke-width": params.FRAME_STROKE_WIDTH_DICT["interchange"],
        })
        for station in self.interchange_stations:
            interchange_station_frame_group.use(station.frame_id_name, station.center_point)
        self.append(interchange_station_frame_group)
        return self

    def add_station_frame(self):
        station_frame_group = Group("station_frame")
        station_frame_group.set_style({
            "fill": params.FRAME_FILL_COLOR,
            "stroke-opacity": params.FRAME_STROKE_OPACITY,
        })
        station_frame_group.use("normal_station_frame")
        station_frame_group.use("interchange_station_frame")
        self.append(station_frame_group)
        return self

    def add_station_point(self):
        for metro in self.metro_objs:
            template = metro.get_station_point()
            self.template_group.append(template)
            
        station_point_group = Group("station_point")
        station_point_group.set_style({
            "fill-opacity": params.STATION_POINT_FILL_OPACITY,
        })
        for station in self.interchange_stations:
            for point_coord, metro in zip(station.point_coords, station.parent_metros):
                station_point_group.use(metro.point_id_name, point_coord)
        self.append(station_point_group)
        return self

