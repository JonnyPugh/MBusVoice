from requests import get
from collections import OrderedDict

class BusInfo(object):
    def __init__(self, favorite_stops=[]):
        self.__favorite_stops = favorite_stops

    def __get_request_json(self, route, params=None):
    	r = get("https://mbus.doublemap.com/map/v2/"+route, params=params)
    	r.raise_for_status()
    	return r.json()

    @property
    def stops(self):
        return {stop["id"]: self.__Stop(stop) for stop in self.__get_request_json("stops")}

    @property
    def buses(self):
        return {bus["id"]: self.__Bus(bus) for bus in self.__get_request_json("buses")}

    @property
    def routes(self):
        return {route["id"]: self.__Route(route) for route in self.__get_request_json("routes")}

    @property
    def etas(self):
    	return {stop: self.get_eta(stop) for stop in self.__favorite_stops}

    def get_eta(self, stop):
        # This is the only route that takes 
        # parameters so it needs to be error checked
        return OrderedDict([(eta["bus_id"], self.__Eta(eta)) for eta in self.__get_request_json("eta", {"stop": stop})["etas"][str(stop)]["etas"]], key=lambda t: t[1].time)

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
            self.route = eta_json["route"]
            self.time = eta_json["avg"]
