'''
File: mqtt_service.py
Created Date: Friday June 13th 2025
Author: Samman Shrestha
Last Modified: We/06/2025 12:27:50
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

import _thread
from usr.extensions.my_mqtts import MyMqttClient
import utime
import usr.Eventstore as Eventstore
from usr.config import Config
import log

cfg = Config.MQTT

mqtt_lock = _thread.allocate_lock()
mqtt_thread_running = False

mqtt_client = None
mqtt_status = "DISCONNECTED"

MQTT_SERVER = cfg["server"]
MQTT_PORT = cfg["port"]
CLIENT_ID = cfg["client_id"]
USERNAME = cfg["username"]
PASSWORD = cfg["password"]
CONFIG_SSL = cfg["ssl_cert"]

SUBSCRIBE_TOPIC = cfg["subscribe_topic"]



def mqtt_err_cb(error):
    """
    Callback function for handling the MQTT thread error occurance
    """
    print(error)
    global mqtt_status
    mqtt_status = "DISCONNECTED"

    global mqtt_client
    mqtt_client.reconnect()

def mqtt_recv_msg_cb(topic, msg):
    """Callback function for received MQTT messages"""
    topic = topic.decode()
    msg = msg.decode()
    
    # Create message object with timestamp
    message_data = {
        'topic': topic,
        'message': msg,
        'timestamp': utime.time(),
    }

    Eventstore.publish("mqtt.message", message_data)

def mqtt_status_cb(status):
    """
    Callback function to handle MQTT connection status changes
    """
    global mqtt_status
    if status == MyMqttClient.CONNECTED:
        mqtt_status = "CONNECTED"
        Eventstore.publish("mqtt.status", "CONNECTED")
    elif status == MyMqttClient.RECONNECTING:
        mqtt_status = "RECONNECTING"
        Eventstore.publish("mqtt.status", "RECONNECTING")
    elif status == MyMqttClient.DISCONNECTED:
        mqtt_status = "DISCONNECTED"
        Eventstore.publish("mqtt.status", "DISCONNECTED")
    elif status == MyMqttClient.FAILED:
        mqtt_status = "FAILED"
        Eventstore.publish("mqtt.status", "FAILED")


def thread_mqtt():
    global mqtt_client, mqtt_status
    mqtt_status = "CONNECTING"
    Eventstore.publish("mqtt.status", "CONNECTING")
    # get the ssl_params data
    certdata = ""
    with open(CONFIG_SSL, "rb") as f:
        certdata = f.read() 

    ssl_params = {
        "cert": certdata
    }

    # Create MQTT client instance
    mqtt_client = MyMqttClient(
        clientid=CLIENT_ID,
        server=MQTT_SERVER,
        port=MQTT_PORT,
        user=USERNAME,
        password=PASSWORD,
        ssl=True,
        ssl_params=ssl_params,
        reconn=False  # Disable automatic reconnection
    )

    mqtt_client.setLogger(log.DEBUG)

    # Set callback functions
    mqtt_client.set_callback(mqtt_recv_msg_cb)
    mqtt_client.set_status_calllabck(mqtt_status_cb)
    mqtt_client.error_register_cb(mqtt_err_cb)

    try:
        print("Connecting to MQTT broker...")
        print("Server: " + MQTT_SERVER + ":" + str(MQTT_PORT))
        print("Client ID: " + CLIENT_ID)
        mqtt_client.connect()

        # Subscribe to topics
        try:
            mqtt_client.subscribe(topic=SUBSCRIBE_TOPIC, qos=1)
            print("Subscribed to: " + SUBSCRIBE_TOPIC)
        except Exception as e:
            print("Failed to subscribe to " + SUBSCRIBE_TOPIC + ": " + str(e))

        # Start the message loop
        mqtt_client.loop_forever()

    except Exception as e:
        print("Failed to connect or subscribe: " + str(e))
        return False

def mqtt_connect():
    global mqtt_thread_running
    Eventstore.publish("load_screen", "MessageScreen")

    def thread_task():
        global mqtt_thread_running
        with mqtt_lock:
            if mqtt_thread_running:
                print("MQTT thread is already running. Skipping new thread start.")
                return
            mqtt_thread_running = True

        try:
            thread_mqtt()
        finally:
            # Reset flag if thread exits
            with mqtt_lock:
                mqtt_thread_running = False

    _thread.start_new_thread(thread_task, ())


def mqtt_disconnect():
    global mqtt_client, mqtt_thread_running
    with mqtt_lock:
        if mqtt_client is not None:
            print("Disconnecting from MQTT broker...")
            try:
                mqtt_client.disconnect()
                mqtt_thread_running = False
                print("MQTT disconnected successfully.")
            except Exception as e:
                print("MQTT disconnect failed: " + str(e))
        else:
            print("MQTT client is not initialized.")


def mqtt_reconnect():
    global mqtt_client, mqtt_thread_running

    with mqtt_lock:
        if mqtt_thread_running:
            print("MQTT is already running. Reconnection skipped.")
            return

        if mqtt_client is not None:
            print("Reconnecting MQTT...")
            try:
                mqtt_client.reconnect()
                mqtt_thread_running = True
                print("MQTT reconnected successfully.")
            except Exception as e:
                print("MQTT reconnection failed: " + str(e))
        else:
            print("MQTT client is not initialized. Starting fresh connection...")
            mqtt_connect()

def mqtt_get_status():
    global mqtt_status
    return mqtt_status
