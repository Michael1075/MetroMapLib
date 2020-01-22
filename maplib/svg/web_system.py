from maplib.svg.svg_element import Group


class WebSystem(Group):
    def __init__(self, id_name, metro_objs, station_objs):
        self.metro_objs = metro_objs
        self.station_objs = station_objs
        Group.__init__(self, id_name)
        self.init_template()
        self.classify_stations()
        self.add_route()
        self.add_normal_station_frame()
        self.add_transfer_station_frame()
        self.add_station_frame()
        self.add_station_point()

    def classify_stations(self):
        self.normal_stations = []
        self.transfer_stations = []
        for station in self.station_objs:
            if station.is_normal:
                self.normal_stations.append(station)
            else:
                self.transfer_stations.append(station)
        return self

    def add_route(self):
        route_group = Group(None)
        route_group.set_style({
            "fill": None,
            "stroke-opacity": self.params.ROUTE_STYLE["stroke_opacity"],
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        route_path_group = Group(None)
        main_route_group = Group(None)
        main_route_group.set_style({
            "stroke-width": self.params.ROUTE_STYLE["stroke_width"],
        })
        sub_route_group = Group(None)
        sub_route_group.set_style({
            "stroke-width": self.params.ROUTE_STYLE["minor_stroke_width"],
        })
        route_mask_group = Group(None)
        route_mask_group.set_style({
            "fill": None,
            "stroke-width": self.params.ROUTE_STYLE["minor_stroke_width"],
            "stroke": self.params.MASK_COLOR,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        })
        for metro in list(reversed(self.metro_objs)):
            route_path = metro.get_route()
            route_path_group.append(route_path)
            if metro.sub_color == "-":
                main_route_group.use_with_style(metro.route_id_name, {
                    "stroke": metro.main_color,
                })
            else:
                mask = metro.get_mask()
                route_mask_group.append(mask)
                main_route_group.use_with_style(metro.route_id_name, {
                    "stroke": metro.main_color,
                    "mask": mask,
                })
                if metro.sub_color != "*":
                    sub_route_group.use_with_style(metro.route_id_name, {
                        "stroke": metro.sub_color,
                    })
        route_group.append(main_route_group)
        route_group.append(sub_route_group)
        self.template.append(route_path_group)
        self.template.append(route_mask_group)
        self.append(route_group)
        return self

    def add_normal_station_frame(self):
        normal_station_frame_template = Group(None)
        for metro in self.metro_objs:
            template_obj = metro.get_normal_station_frame()
            normal_station_frame_template.append(template_obj)
        self.template.append(normal_station_frame_template)
        normal_station_frame_group = Group("normal_station_frame")
        normal_station_style_dict = {
            "stroke-width": self.params.STATION_FRAME_STYLE["stroke_width"]["normal"],
        }
        normal_station_body_stroke_color = self.params.STATION_FRAME_STYLE["stroke_color"]["normal"]
        if normal_station_body_stroke_color is not None:
            normal_station_style_dict["stroke"] = normal_station_body_stroke_color
        normal_station_frame_group.set_style(normal_station_style_dict)
        for station in self.normal_stations:
            normal_station_frame_group.use(station.parent_metro.frame_id_name, station.center_point)
        self.append(normal_station_frame_group)
        return self

    def add_transfer_station_frame(self):
        station_type_set = set()
        template_list = []
        for station in self.transfer_stations:
            if station.station_type not in station_type_set:
                station_type_set.add(station.station_type)
                template_obj = station.get_transfer_station_frame()
                template_list.append(template_obj)
        template_list.sort(key = lambda template_obj: template_obj.id_name)
        transfer_station_frame_template = Group(None)
        for template_obj in template_list:
            transfer_station_frame_template.append(template_obj)
        self.template.append(transfer_station_frame_template)
        transfer_station_frame_group = Group("transfer_station_frame")
        transfer_station_frame_group.set_style({
            "stroke": self.params.STATION_FRAME_STYLE["stroke_color"]["transfer"],
            "stroke-width": self.params.STATION_FRAME_STYLE["stroke_width"]["transfer"],
        })
        for station in self.transfer_stations:
            transfer_station_frame_group.use(station.frame_id_name, station.center_point)
        self.append(transfer_station_frame_group)
        return self

    def add_station_frame(self):
        station_frame_group = Group("station_frame")
        station_frame_group.set_style({
            "fill": self.params.STATION_FRAME_STYLE["fill_color"],
            "fill-opacity": self.params.STATION_FRAME_STYLE["fill_opacity"],
            "stroke-opacity": self.params.STATION_FRAME_STYLE["stroke_opacity"],
        })
        station_frame_group.use("normal_station_frame")
        station_frame_group.use("transfer_station_frame")
        self.append(station_frame_group)
        return self

    def add_station_point(self):
        station_point_template = Group(None)
        for metro in self.metro_objs:
            template_obj = metro.get_station_point()
            station_point_template.append(template_obj)
        self.template.append(station_point_template)
        station_point_group = Group("station_point")
        station_point_group.set_style({
            "fill-opacity": self.params.STATION_POINT_STYLE["fill_opacity"],
        })
        for station in self.transfer_stations:
            for point_coord, metro in zip(station.point_coords, station.parent_metros):
                station_point_group.use(metro.point_id_name, point_coord)
        self.append(station_point_group)
        return self
