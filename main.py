from Backhaul import Backhaul
import json
import threading
from Node import Node


def update_nodes_info(nodes):
    users_info = json.load(open('./data/users_info.json'))['users']
    for node in nodes:
        info = users_info[node.callsign]
        node.gid = info['gid']
        node.end_coordinates = info['end_location']


if __name__ == "__main__":
    ## 1. Create 200 backhaul _data location instances, need to save in dictionary.
    users_info = data = json.load(open('./data/users_info.json'))['users'].keys()  # get users call signs
    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes)
    test1 = Backhaul()
    test1.create_20_location_instances(nodes)

    # 2. update all fields for each user.
    test1.update_users_starting_info(nodes) #update nodes starting information

    # 3 get all users route path
    test1.update_users_route(nodes)

    # get each nodes tokens
    test1.get_users_tokens(nodes)

    list_of_threads = [threading.Thread(target=test1.scheduler, args=(node,)) for node in nodes]
    for thread in list_of_threads:
        thread.start()
    for thread in list_of_threads:
        thread.join()
        
        

