from requests import Session

class BusInfo(object):
    def __init__(self, favorite_stops=[]):
        self.__favorite_stops = favorite_stops
        self.__session = Session()
        self.__stops = None
        self.__buses = None
        self.__routes = None
        self.__etas = None

    def __get_request_json(self, route, params=None):
    	r = self.__session.get("https://mbus.doublemap.com/map/v2/"+route, params=params)
    	r.raise_for_status()
    	return r.json()

    @property
    def stops(self):
        if not self.__stops:
            self.__stops = {stop["id"]: self.__Stop(stop) for stop in self.__get_request_json("stops")}
        return self.__stops

    @property
    def stops_by_name(self):
        return {stop.name.lower(): [stop_id] for stop_id, stop in self.stops.items()}

    @property
    def buses(self):
        if not self.__buses:
            self.__buses = {bus["id"]: self.__Bus(bus) for bus in self.__get_request_json("buses")}
        return self.__buses

    @property
    def routes(self):
        if not self.__routes:
            self.__routes = {route["id"]: self.__Route(route) for route in self.__get_request_json("routes")}
        return self.__routes

    @property
    def etas(self):
        if not self.__etas:
            self.__etas = {stop: self.get_eta(stop) for stop in self.__favorite_stops}
    	return self.__etas

    def get_eta(self, stop):
        eta_json = self.__get_request_json("eta", {"stop": stop})
        if "error" in eta_json:
            # If the stop number is invalid, the JSON will contain "error"
            raise InvalidStop(stop)
        
        return sorted([self.__Eta(eta) for eta in eta_json["etas"][str(stop)]["etas"]], key=lambda eta: eta.time)

    class __Stop(object):
        def __init__(self, stop_json):
            self.name = stop_json["name"]
            self.description = stop_json["description"]
            self.latitude = stop_json["lat"]
            self.longitude = stop_json["lon"]
            self.buddy = stop_json["buddy"]

    class __Bus(object):
        def __init__(self, bus_json):
            self.latitude = bus_json["lat"]
            self.longitude = bus_json["lon"]
            self.next_stop = bus_json["heading"]
            self.route = bus_json["route"]
            self.prev_stop = bus_json["lastStop"]

    class __Route(object):
        def __init__(self, route_json):
            self.name = route_json["name"]
            self.description = route_json["description"]
            self.start_time = route_json["start_time"]
            self.end_time = route_json["end_time"]
            self.stops = route_json["stops"]

    class __Eta(object):
        def __init__(self, eta_json):
            self.bus_id = eta_json["bus_id"]
            self.route = eta_json["route"]
            self.time = eta_json["avg"]

class InvalidStop(Exception):
    def __init__(self, stop):
        super(InvalidStop, self).__init__("There is no stop with the ID "+str(stop))
