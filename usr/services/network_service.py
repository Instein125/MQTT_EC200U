'''
File: network_service.py
Created Date: Friday June 13th 2025
Author: Samman Shrestha
Last Modified: We/06/2025 11:18:01
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

from usr.extensions.my_netmanager import MyNetManager
import usr.Eventstore as Eventstore

_net = MyNetManager()


def net_event_callback(args):
    """
    Callback function to handle network state changes
    Args:
        args: Tuple containing (profile_id, network_state, additional_info)
    """
    profile_id, net_state = args[0], args[1]

    if net_state == 1:
        Eventstore.publish("network.status", "CONNECTED")
    else:
        Eventstore.publish("network.status", "DISCONNECTED")


def init():
    conn_result = _net.net_connect()
    if conn_result == 0:
        if _net.set_callback(net_event_callback):
            print("Callback registered successfully")
        Eventstore.publish("network.status", "CONNECTED")
    return conn_result


def get_netmanager():
    return _net
