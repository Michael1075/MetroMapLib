import maplib.parameters as params

from maplib.svg.svg_element import Group


class WebSystem(Group):
    def __init__(self, id_name, metro_objs, station_objs):
        self.metro_objs = metro_objs
        self.station_objs = station_objs
        Group.__init__(self, id_name)
        self.init_template()
        self.classify_stations()
        self.def_mask_rect()
        self.add_route()
        self.add_normal_station_frame()
        self.add_interchange_station_frame()
        self.add_station_frame()
        self.add_station_point()

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
        mask_rect_group.use_with_style("body_rect", {
            "fill": params.MASK_BASE_COLOR,
        })
        self.template.append(mask_rect_group)

    def add_route(self):
        route_mask_group = Group("route_mask")
        route_mask_group.set_style({
            "fill": None,
            "stroke-width": params.ROUTE_STYLE["minor_stroke_width"],
            "stroke": params.MASK_COLOR,
        })
        for metro in self.metro_objs:
            route_path_template = metro.get_route()
            self.template.append(route_path_template)
            if metro.sub_color is not None:
                mask_template = metro.get_mask()
                metro.set_mask(mask_template)
                route_mask_group.append(mask_template)
        self.template.append(route_mask_group)

        route_group = Group("route")
        route_group.set_style({
            "fill": None,
            "stroke-opacity": params.ROUTE_STYLE["stroke_opacity"],
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        main_route_group = Group("main_route")
        main_route_group.set_style({
            "stroke-width": params.ROUTE_STYLE["stroke_width"],
        })
        sub_route_group = Group("sub_route")
        sub_route_group.set_style({
            "stroke-width": params.ROUTE_STYLE["minor_stroke_width"],
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
            template_obj = metro.get_normal_station_frame()
            self.template.append(template_obj)

        normal_station_frame_group = Group("normal_station_frame")
        normal_station_style_dict = {
            "stroke-width": params.STATION_FRAME_STYLE["stroke_width"]["normal"],
        }
        normal_station_body_stroke_color = params.STATION_FRAME_STYLE["stroke_color"]["normal"]
        if normal_station_body_stroke_color is not None:
            normal_station_style_dict["stroke"] = normal_station_body_stroke_color
        normal_station_frame_group.set_style(normal_station_style_dict)
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
                template_obj = station.get_interchange_station_frame()
                template_list.append(template_obj)
        template_list.sort(key = lambda template_obj: template_obj.id_name)
        for template_obj in template_list:
            self.template.append(template_obj)

        interchange_station_frame_group = Group("interchange_station_frame")
        interchange_station_frame_group.set_style({
            "stroke": params.STATION_FRAME_STYLE["stroke_color"]["interchange"],
            "stroke-width": params.STATION_FRAME_STYLE["stroke_width"]["interchange"],
        })
        for station in self.interchange_stations:
            interchange_station_frame_group.use(station.frame_id_name, station.center_point)
        self.append(interchange_station_frame_group)
        return self

    def add_station_frame(self):
        station_frame_group = Group("station_frame")
        station_frame_group.set_style({
            "fill": params.STATION_FRAME_STYLE["fill_color"],
            "fill-opacity": params.STATION_FRAME_STYLE["fill_opacity"],
            "stroke-opacity": params.STATION_FRAME_STYLE["stroke_opacity"],
        })
        station_frame_group.use("normal_station_frame")
        station_frame_group.use("interchange_station_frame")
        self.append(station_frame_group)
        return self

    def add_station_point(self):
        for metro in self.metro_objs:
            template_obj = metro.get_station_point()
            self.template.append(template_obj)
            
        station_point_group = Group("station_point")
        station_point_group.set_style({
            "fill-opacity": params.STATION_POINT_STYLE["fill_opacity"],
        })
        for station in self.interchange_stations:
            for point_coord, metro in zip(station.point_coords, station.parent_metros):
                station_point_group.use(metro.point_id_name, point_coord)
        self.append(station_point_group)
        return self
