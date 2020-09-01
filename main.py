import requests
import struct
from credentials import Cred
from gen.portal_pb2 import PBBackhaulResponse
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime


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
    temp = get_user_info(location, coordinates)

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


def get_user_info(location, coordinates):
    """
    Returns serialized user data for one node
    :param coordinates:
    :param location:
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

    temp_data = get_route_coordinates()  # list of list
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


def get_route_coordinates():
    data = None
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    base_url = 'https://api.openrouteservice.org'
    api_key = '5b3ce3597851110001cf6248d4c71ce7a2854a8db35ac96903e7fed3'

    try:
        r = requests.get(
            f'{base_url}/v2/directions/driving-car?api_key={api_key}&start=-73.860208,%2040.755835&end=-73.954549,%2040.699929',
            headers=headers)
        data = r.json()
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
    except requests.exceptions.ConnectionError as err:
        print("Error connecting:", err)

    return data['features'][0]['geometry']['coordinates']


########################################################################################################################


"""
A PBBackhaulResponse will create a backhaul object where we can add shapes,
pins, user locations, and messages. This will be serialized and sent to the backhaul api
"""
backhaul_data = PBBackhaulResponse()

"""
PLI header
A header can be added to shapes, pins, and user_locations. It consists of:
id (optional) - int
gid (optional) - int
timestamp (optional) - double
name (optional) - string
callsign (optional) - string
All fields are optional but must follow the correct type.
This doesn't mean it will pass portal's request validation
"""

"""
Create a user location
A user location has a header (optional) and a locationData (optional)
A locationData contains:
    - coordinate (optional)
    - pli_location_accuracy (optional)
"""
''''''
# Add user location to backhaul
location = backhaul_data.locations.add()
scheduler(location)








