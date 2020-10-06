from Backhaul import Backhaul
import json
import threading
from Node import Node
from portal_pb2 import PBBackhaulResponse


def update_nodes_info(nodes,number_of_users):
    users_info = json.load(open('./data/users_info.json'))['users']
    for i in range(number_of_users):
        node = nodes[i]
        info = users_info[node.callsign]
        node.gid = info['gid']
        node.end_coordinates = info['end_location']

def start_threads(function, arg):
    list_of_threads = [threading.Thread(target=function, args=(node,)) for node in arg]
    for thread in list_of_threads:
        thread.start()
    for thread in list_of_threads:
        thread.join()

def set_users_gid_in_portal(nodes: list, number_of_users):
    test = Backhaul()
    for i in range(number_of_users):
        node = nodes[i]
        print('Setting gid:',node.callsign, end='\n')
        test.set_gid(node)


def test_pli_backhaul(number_of_users):
    ## 1. Create 20 backhaul _data location instances, need to save in dictionary.
    users_info = list(json.load(open('./data/users_info.json'))['users'].keys())[0:number_of_users]  # get users call signs
    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes, number_of_users)
    test1 = Backhaul(number_of_users)
    test1.create_location_instances(nodes)

    # 2. update all fields for each user.
    test1.update_users_starting_info(nodes)  # update nodes starting information
    # 3 get all users route path
    test1.update_users_route(nodes)
    # 4 get each nodes tokens
    test1.get_users_tokens(nodes)
    # 5 set users gid in the portal
    set_users_gid_in_portal(nodes, number_of_users)
    # 6 start threads
    start_threads(test1.pli_scheduler, nodes)

def test_backhaul_messages(number_of_networks):
    users_info = list(json.load(open('./data/users_info.json'))['users'].keys())[0:number_of_networks]# get users call signs
    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes, number_of_networks)
    test1 = Backhaul(number_of_networks)
    test1.create_message_instances(nodes)

    # 4 get each nodes tokens
    test1.get_users_tokens(nodes)
    # 5 set users gid in the portal
    set_users_gid_in_portal(nodes, number_of_networks)

    # 6 start threads
    start_threads(test1.message_scheduler, nodes)


def test_backhaul_shapes(number):
    users_info = list(json.load(open('./data/users_info.json'))['users'].keys())[0:number]  # get users call signs

    nodes = [Node(callsign) for callsign in users_info]
    update_nodes_info(nodes, number)
    test1 = Backhaul(number)
    test1.update_nodes_backhaulResponse(nodes)  # each node has a backhaul response node
    test1.get_users_tokens(nodes)
    # 5 set users gid in the portal
    set_users_gid_in_portal(nodes, number)

    list_of_threads = [threading.Thread(target=test1.shape_scheduler, args=(nodes, node)) for node in nodes]
    for thread in list_of_threads:
        thread.start()
    for thread in list_of_threads:
        thread.join()

if __name__ == "__main__":
    #test_backhaul_messages(5)
    #test_pli_backhaul(5)
    #test_backhaul_shapes()
    number = 3
    #est_pli_backhaul(number)
    #test_backhaul_messages(5)
    test_backhaul_shapes(number)

















        
        

