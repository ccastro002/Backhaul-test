class Node(object):
    def __init__(self, callsign):
        self.callsign = callsign
        self.token = ''
        self.gid = None
        self.route_path = []
        self.end_coordinates = None
        self.backhaul_response = None
        self.location_headers = None