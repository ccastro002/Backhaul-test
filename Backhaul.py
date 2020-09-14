import threading

import requests
import struct
from credentials import Cred
from gen.portal_pb2 import PBBackhaulResponse
import time
from datetime import datetime
import json
import random


class Backhaul():

    def __init__(self, number=0):
        self.number = number
        self.base_url = 'https://portal-stage.gotennapro.com'

    def coords_to_binary(self, coordinates):
        """
        Converts coordinates to a byte string
        This how mobile currently handles their converting their coordinates
        """
        [latitude, longitude] = coordinates
        latitude_binary = struct.pack('<d', latitude)
        longitude_binary = struct.pack('<d', longitude)
        return latitude_binary + longitude_binary

    def multi_coords_to_binary(self, coordinates):
        """
        Converts a list of coordinates into a byte string
        Reimplements mobile's algorithm
        """

        multi_coords_binary = bytes()
        for coord in coordinates:
            lat_long_binary = self.coords_to_binary(
                [coord['latitude'], coord['longitude']])
            multi_coords_binary += lat_long_binary

        return multi_coords_binary

    def hex_to_dec(self, hexadec):
        """
        Colors are all in decimal format so we can use this to convert hex values
        of colors to decimal. You can also use an online converter.
        The FF needs to be appended because the values mobile uses are in
        ARGB format (for example FFFF00FF)
        """
        alpha = 'FF'
        return int(alpha + hexadec, base=16)

    def set_gids(self, node):
        headers = {
            'Authorization': 'Bearer {token}'.format(token=node.token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = {"gid": node.gid}
        print(data)

        try:
            r = requests.put(f'{self.base_url}/api/v2/user/gid', headers=headers, data=json.dumps(data,))
            print('status code: {}'.format(r.status_code))
            print('Text: {}'.format(r.text))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err.response.text)
        except requests.exceptions.ConnectionError as err:
            print("Error connecting:", err)

    def pli_backhaul(self, node, coordinates):
        """
        This function receives a serialized binary string data that will be backhauled to the /api/v2/backhaul endpoint
        :return: void
        """

        temp = self.update_user_info(node, coordinates)
        token = node.token
        self.backhaul(temp, token)

    def backhaul(self, data, token):
        headers = {
            'Authorization': 'Bearer {token}'.format(token=token),
            'Content-Type': 'application/protobuf',
            'Accept': 'application/json'
        }

        try:
            r = requests.post(f'{self.base_url}/api/v2/backhaul', headers=headers, data=data)
            print('status code: {}'.format(r.status_code))
            print('Text: {}'.format(r.text))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err.response.text)
        except requests.exceptions.ConnectionError as err:
            print("Error connecting:", err)

    def get_timestamp(self):
        """
        Return the current timestamp
        :return: timestamp
        """
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return timestamp

    def update_user_info(self, node, coordinates):
        """
        Returns serialized user data for one node
        :param coordinates:
        :param location - pli header:
        PLI header - A header can be added to shapes, pins, and user_locations. It consists of:
        id (optional) - int
        gid (optional) - int
        timestamp (optional) - double
        name (optional) - string
        callsign (optional) - string
        All fields are optional but must follow the correct type.
        This doesn't mean it will pass portal's request validation
        :return:
        """
        # Update user location with info
        node.location_headers.header.timestamp = self.get_timestamp()  # double
        node.location_headers.header.gid = node.gid  # int
        node.location_headers.header.callsign = node.callsign  # string
        node.location_headers.locationData.coordinate = self.coords_to_binary(
            [coordinates[0], coordinates[1]])  # bytes
        node.location_headers.locationData.pli_location_accuracy = 65  # int

        # Must be serialized to buffer so it can be sent to backhaul
        return node.backhaul_response.SerializeToString()

    def pli_scheduler(self, node):
        '''
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(backhaul, 'interval', minutes=1, args=[location])
        sched.start() '''
        print('Press Ctrl+{0} to exit'.format('C'))
        index = 0
        try:
            while True:
                if index > len(node.route_path):
                    print('User at final position', end='\n')
                    break
                coordinate = node.route_path[index]  # returns a lit 1 is lat and 0 is long
                coordinates = (coordinate[1], coordinate[0])
                self.pli_backhaul(node, coordinates)
                index += 1
                time.sleep(59)
                print(node.callsign, 'first round', end='\n')
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            # sched.shutdown()
            print('Stopping backhaul')

    def get_route_coordinates(self, start_coordinates: tuple, end_coordinates: tuple):
        cred = Cred('')
        data = None
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        }
        base_url = 'https://api.openrouteservice.org'

        try:
            r = requests.get(
                f"{base_url}/v2/directions/foot-walking?api_key={cred.api_key}&start={start_coordinates[1]},"
                f"{start_coordinates[0]}&end={end_coordinates[1]},{end_coordinates[0]}",
                headers=headers)
            data = r.json()
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err.response.text)
        except requests.exceptions.ConnectionError as err:
            print("Error connecting:", err)

        return data['features'][0]['geometry']['coordinates']

    def create_location_instances(self, node_list: list):
        """
           A PBBackhaulResponse will create a backhaul object where we can add shapes,
           pins, user locations, and messages. This will be serialized and sent to the backhaul api. Based
           on the lenth of the node list thats how many instance this function will create.
        """
        for node in node_list[0:self.number]:
            backhaul = PBBackhaulResponse()
            location = backhaul.locations.add()
            node.backhaul_response, node.location_headers = backhaul, location
            print(type(node.backhaul_response))

    def update_users_starting_info(self, nodes: list):
        for node in nodes[:self.number]:
            node.location_headers.header.timestamp = self.get_timestamp()  # double
            node.location_headers.header.gid = node.gid
            node.location_headers.header.callsign = node.callsign
            node.location_headers.locationData.coordinate = self.coords_to_binary(
                [40.893985, -73.884962])  # bytes
            node.location_headers.locationData.pli_location_accuracy = 65

    def update_users_route(self, nodes: list):
        user_routes = {}

        for node in nodes[0:self.number]:
            coordinates = node.end_coordinates
            end_coordinates = (coordinates['lat'], coordinates['long'])
            node.route_path = self.get_route_coordinates((40.893985, -73.884962), end_coordinates)
            print(node.route_path)
        return user_routes

    def get_users_tokens(self, nodes: list):
        '''Returns a dictionary with tokens'''
        for node in nodes[:self.number]:
            cred = Cred(node.callsign)
            node.token = cred.get_token()

    def get_random_id(self):
        return random.randint(10000000000000, 99999999999999)

    def message_backhaul(self, node, message):

        # # Update message with info
        node.message_header.header.id = self.get_random_id()  # int
        node.message_header.header.timestamp = self.get_timestamp()  # double
        node.message_header.header.gid = node.gid  # int
        node.message_header.header.callsign = node.callsign  # string
        node.message_header.header.name = node.callsign  # string

        node.message_header.text = message

        return node.backhaul_response.SerializeToString()

    def message_scheduler(self, node):
        print('Press Ctrl+{0} to exit'.format('C'))
        try:
            for i in range(0, 101):
                message = node.callsign + ': ' + str(time.time())
                print(f'{node.callsign} backhauling message: {message}', end='\n')
                data = self.message_backhaul(node, message)  # nee to get serialized data , then backhaul
                self.backhaul(data, node.token)
                time.sleep(59)

        except (KeyboardInterrupt, SystemExit):
            print('Stopping backhaul')

    def create_message_instances(self, nodes: list):
        for node in nodes[0:self.number]:
            backhaul_data = PBBackhaulResponse()
            message = backhaul_data.messages.add()
            node.backhaul_response = backhaul_data
            node.message_header = message

########################################################################################################################
