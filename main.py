import requests
import struct
from credentials import Cred
from gen.portal_pb2 import PBBackhaulResponse
import time
from datetime import datetime
import json
import os


def coords_to_binary(coordinates):
    """
    Converts coordinates to a byte string
    This how mobile currently handles their converting their coordinates
    """
    [latitude, longitude] = coordinates
    latitude_binary = struct.pack('<d', latitude)
    longitude_binary = struct.pack('<d', longitude)
    return latitude_binary + longitude_binary


def multi_coords_to_binary(coordinates):
    """
    Converts a list of coordinates into a byte string
    Reimplements mobile's algorithm
    """

    multi_coords_binary = bytes()
    for coord in coordinates:
        lat_long_binary = coords_to_binary(
            [coord['latitude'], coord['longitude']])
        multi_coords_binary += lat_long_binary

    return multi_coords_binary


def hex_to_dec(hexadec):
    """
    Colors are all in decimal format so we can use this to convert hex values
    of colors to decimal. You can also use an online converter.
    The FF needs to be appended because the values mobile uses are in
    ARGB format (for example FFFF00FF)
    """
    alpha = 'FF'
    return int(alpha + hexadec, base=16)


def backhaul(location, coordinates: tuple):
    """
    This function receives a serialized binary string data that will be backhauled to the /api/v2/backhaul endpoint
    :return: void
    """
    cred = Cred()
    token = cred.get_token()
    temp = update_user_info(location, coordinates)

    headers = {
        'Authorization': 'Bearer {token}'.format(token=token),
        'Content-Type': 'application/protobuf',
        'Accept': 'application/json'
    }

    try:
        r = requests.post('https://portal-stage.gotennapro.com/api/v2/backhaul', headers=headers, data=temp)
        print('status code: {}'.format(r.status_code))
        print('Text: {}'.format(r.text))
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
    except requests.exceptions.ConnectionError as err:
        print("Error connecting:", err)


def get_timestamp():
    """
    Return the current timestamp
    :return: timestamp
    """
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return timestamp


def update_user_info(location, coordinates) -> object:
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
    location.header.timestamp = get_timestamp()  # double
    location.header.gid = 92190340361517  # int
    location.header.callsign = "Christian"  # string
    location.locationData.coordinate = coords_to_binary(
        [coordinates[0], coordinates[1]])  # bytes
    location.locationData.pli_location_accuracy = 65  # int

    # Must be serialized to buffer so it can be sent to backhaul
    return backhaul_data.SerializeToString()


def scheduler(location):
    '''
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(backhaul, 'interval', minutes=1, args=[location])
    sched.start() '''
    print('Press Ctrl+{0} to exit'.format('C'))

    temp_data = get_route_coordinates((40.893985, -73.884962),(40.634930, -73.964389))  # list of list  TODO fix this
    index = 0
    try:
        while True:
            coordinate = temp_data[index]  # returns a lit 1 is lat and 0 is long
            coordinates = (coordinate[1], coordinate[0])
            backhaul(location, coordinates)
            index += 1
            time.sleep(59)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        # sched.shutdown()
        print('Stopping backhaul')


def get_route_coordinates(start_coordinates: tuple, end_coordinates: tuple):
    cred = Cred()
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


def create_100_location_instances(backhaul_pbb):
    pli_locations = {}
    """
       A PBBackhaulResponse will create a backhaul object where we can add shapes,
       pins, user locations, and messages. This will be serialized and sent to the backhaul api
    """
    for i in range(0, 100):
        user = f'node{i}'
        location = backhaul_pbb.locations.add()
        pli_locations[user] = location

    return pli_locations


def update_users_starting_info(users_pli):
    data = json.load(open('./data/users_info.json'))['users']  #dictionary

    for callsign, location in users_pli.items():
        user_info = data[callsign]
        location.header.timestamp = get_timestamp()  # double
        location.header.gid = user_info['gid']
        location.header.callsign = callsign
        location.locationData.coordinate = coords_to_binary(
            [40.893985, -73.884962])  # bytes
        location.locationData.pli_location_accuracy = 65


    ########################################################################################################################
if __name__ == "__main__":
    backhaul_data = PBBackhaulResponse()
    ## 1. Create 200 backhaul _data location instances, need to save in dictionary.
    #temp = create_100_location_instances(backhaul_data)
    #update_users_starting_info(temp)
    #scheduler(temp['node0'])


    # update all fields for each user.








# Add user location to backhaul    starting location for everoyone 40.893985, -73.884962
#location = backhaul_data.locations.add()
#scheduler(location)








