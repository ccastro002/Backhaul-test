import requests
import struct
from credentials import Cred
from gen.portal_pb2 import PBBackhaulResponse


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



def backhaul(to_binary_string):
    """
    This function receives a serialized binary string data that will be backhauled to the /api/v2/backhaul endpoint
    :param to_binary_string:
    :return: void
    """
    cred = Cred()
    token = cred.get_token()

    headers = {
        'Authorization': 'Bearer {token}'.format(token=token),
        'Content-Type': 'application/protobuf',
        'Accept': 'application/json'
    }

    try:
        r = requests.post('https://portal-stage.gotennapro.com/api/v2/backhaul', headers=headers, data=to_binary_string)
        print('status code: {}'.format(r.status_code))
        print('Text: {}'.format(r.text))
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err.response.text)
    except requests.exceptions.ConnectionError as err:
        print("Error connecting:", err)







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

# Update user location with info
location.header.timestamp = 1628873628  # double
location.header.gid = 92190340361517  # int
location.header.callsign = "Christian"  # string
location.locationData.coordinate = coords_to_binary(
    [40.755994, -73.860577])  # bytes
location.locationData.pli_location_accuracy = 65  # int


# Must be serialized to buffer so it can be sent to backhaul
to_binary_string = backhaul_data.SerializeToString()




########################################################################################################################
backhaul(to_binary_string)



