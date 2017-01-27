from requests import get

class BusInfo(object):
    def __init__(self, favorite_stops=[]):
        self.__favorite_stops = favorite_stops

    def __get_request_json(self, route, params=None):
    	r = get("https://mbus.doublemap.com/map/v2/"+route, params=params)
    	r.raise_for_status()
    	return r.json()

    @property
    def stops(self):
    	return self.__get_request_json("stops")

    @property
    def buses(self):
    	return self.__get_request_json("buses")

    @property
    def routes(self):
    	return self.__get_request_json("routes")

    @property
    def etas(self):
    	return {stop: self.get_eta(stop) for stop in self.__favorite_stops}

    def get_eta(self, stop):
        # This is the only route that takes 
        # parameters so it needs to be error checked
    	return self.__get_request_json("eta", {"stop": stop})
