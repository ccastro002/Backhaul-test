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

def start_threads(function, arg):
    list_of_threads = [threading.Thread(target=function, args=(node,)) for node in arg]
    for thread in list_of_threads:
        thread.start()
    for thread in list_of_threads:
        thread.join()

def set_users_gid_in_portal(nodes: list):
    test = Backhaul()
    for node in nodes:
        test.set_gids(node)


def test_pli_backhaul():
    ## 1. Create 20 backhaul _data location instances, need to save in dictionary.
    users_info = json.load(open('./data/users_info.json'))['users'].keys()  # get users call signs
    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes)
    test1 = Backhaul(20)
    test1.create_location_instances(nodes)

    # 2. update all fields for each user.
    test1.update_users_starting_info(nodes)  # update nodes starting information

    # 3 get all users route path
    test1.update_users_route(nodes)

    # 4 get each nodes tokens
    test1.get_users_tokens(nodes)

    # 5 start threads
    start_threads(test1.pli_scheduler, nodes)

def test_backhaul_messages():
    users_info = list(json.load(open('./data/users_info.json'))['users'].keys())[0:5]  # get users call signs
    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes)
    test1 = Backhaul(5)
    test1.create_message_instances(nodes)

    # 4 get each nodes tokens
    test1.get_users_tokens(nodes)
    # 5 set users gid in the portal
    set_users_gid_in_portal(nodes)

    # 6 start threads
    start_threads(test1.message_scheduler, nodes)

if __name__ == "__main__":
    test_backhaul_messages()






        
        

