import utime
import log
import net
import _thread
import dataCall
import uos
from umqtt import MQTTClient

# Application version
APP_VERSION = "1.0.0"


def get_version():
    return APP_VERSION

# Reclaim the thread resource through the status after calling MQTTClient.disconnect().
TaskEnable = True

# Encapsulate MQTT so it can support more custom logic.
class MyMqttClient():
    '''
    mqtt init
    '''

    """
    WifiManager class for ESP32
    """
    # MQTT connection status
    CONNECTED = 0     # MQTT Connected
    RECONNECTING = 1    # MQTT attempting to reconnect
    DISCONNECTED = -1      # MQTT DISCONNECTED
    FAILED = -2       # MQTT FAILED CONNECTION

    # Note: The parameter reconn enables or disables the internal reconnection mechanism. Default value: True (enable).
    # If you need to test or use the external reconnection mechanism, please refer to this example code below. Before testing, set reconn to False, otherwise, the internal reconnection mechanism will be used by default.
    def __init__(self, clientid, server, port, user=None, password=None, keepalive=0, ssl=False, ssl_params={},
                 reconn=True):
        self.logger = None
        self.__clientid = clientid
        self.__pw = password
        self.__server = server
        self.__port = port
        self.__uasename = user
        self.__keepalive = keepalive
        self.__ssl = ssl
        self.__ssl_params = ssl_params
        self.topics = []
        self.qos = None
        # Network status flag.
        self.__nw_flag = True
        # Create a mutex.
        self.mp_lock = _thread.allocate_lock()
        # Create a class to initialize the MQTT object.
        self.client = MQTTClient(self.__clientid, self.__server, self.__port, self.__uasename, self.__pw,
                                 keepalive=self.__keepalive, ssl=self.__ssl, ssl_params=self.__ssl_params,
                                 reconn=reconn)
        self.__status_cb = None

    def setLogger(self, level):
        """
        Set up logging configuration
        Args:
            log level (str): log level.
        """
        self.logger = log.getLogger(self.__class__.__name__)
        self.logger.setLevel(level)

    def connect(self):
        '''
        Connect to the MQTT server.
        '''
        try:  
            ret = self.client.connect()
            if ret == 0:
                if self.__status_cb:
                    self.__status_cb(self.CONNECTED)

            # Register the callback function of network status. When the network status changes, the function will be called.
            flag = dataCall.setCallback(self.nw_cb)
            if flag != 0:
                # The network callback registration failed.
                raise Exception("Network callback registration failed")
            
        except Exception as e:
            if self.__status_cb:
                    self.__status_cb(self.FAILED)
            raise

    def set_callback(self, sub_cb):
        '''
        Set the callback function of receiving messages.
        '''
        self.client.set_callback(sub_cb)

    def set_status_calllabck(self, status_cb):
        '''
        Set the callback function for mqtt status
        '''
        self.__status_cb = status_cb

    def error_register_cb(self, func):
        '''
        Set the callback function of receiving MQTT thread error occurrence.
        '''
        self.client.error_register_cb(func)

    def subscribe(self, topic, qos=0):
        '''
        Subscribe to a topic or list of topics.

        Args:
            topic (str or list of str): Topic(s) to subscribe to.
            qos (int): Quality of Service level (default: 0)

        Raises:
            ValueError: If topic type is invalid or subscription fails.
        '''
        if not hasattr(self, 'topics'):
            self.topics = []  # Ensure it's initialized

        try:
            if isinstance(topic, str):
                self.client.subscribe(topic, qos)
                self.topics.append(topic)
            elif isinstance(topic, list):
                for t in topic:
                    if not isinstance(t, str):
                        raise ValueError("Invalid topic in list: %s" % str(t))
                    self.client.subscribe(t, qos)
                    self.topics.append(t)
            else:
                raise ValueError("Topic must be a string or a list of strings.")

        except Exception as e:
            if self.logger is not None:
                self.logger.error("MQTT subscription failed: %s" % str(e))
            raise ValueError("Failed to subscribe to topic(s): %s" % str(e))


    def publish(self, topic, msg, qos=0):
        '''
        Publish a message to a topic.

        Args:
            topic (str): Topic to publish to.
            msg (str): Message payload.
            qos (int): Quality of Service level (default: 0).

        Returns:
            bool: True if published successfully, False otherwise.
        '''
        try:
            return self.client.publish(topic, msg, qos)
        except Exception as e:
            log.error("Failed to publish message to topic '%s': %s" % (topic, str(e)))
            return False

    def disconnect(self):
        '''
        Disconnect from the MQTT server.
        '''
        global TaskEnable
        # Close the monitoring thread of wait_msg.
        TaskEnable = False
        # Disconnect from the MQTT server and release the resources.
        self.client.disconnect()
        if self.__status_cb:
            self.__status_cb(self.DISCONNECTED)

    def reconnect(self):
        '''
        MQTT reconnection mechanism.

        This function ensures safe reconnection to the MQTT server. It will:
        - Wait for network and data call to be ready.
        - Reconnect the MQTT client.
        - Resubscribe to all previously subscribed topics.

        Returns:
            bool: True if reconnection and subscription succeed, False otherwise.
        '''
        if self.mp_lock.locked():
            if self.logger is not None:
                self.logger.info("Reconnection already in progress.")
            return False

        self.mp_lock.acquire()
        try:
            if self.__status_cb:
                self.__status_cb(self.RECONNECTING)

            if self.logger is not None:
                self.logger.info("Closing previous MQTT connection.")
            self.client.close()

            while True:
                net_sta = net.getState()
                if net_sta != -1 and net_sta[1][0] == 1:
                    call_state = dataCall.getInfo(1, 0)
                    if call_state != -1 and call_state[2][0] == 1:
                        try:
                            if self.logger is not None:
                                self.logger.info("Network ready. Attempting MQTT reconnection.")
                            self.connect()

                        except Exception as e:
                            if self.logger is not None:
                                self.logger.error("MQTT connection failed: %s" % str(e))
                            self.client.close()

                            utime.sleep(5)
                            continue

                        # Resubscribe to topics
                        try:
                            if hasattr(self, 'topics') and isinstance(self.topics, list):
                                for t in self.topics:
                                    try:
                                        self.client.subscribe(t, self.qos)
                                        if self.logger is not None:
                                            self.logger.info("Resubscribed to topic: %s" % t)
                                    except Exception as sub_e:
                                        if self.logger is not None:
                                            self.logger.error("Failed to resubscribe to topic '%s': %s" % (t, str(sub_e)))
                            elif isinstance(self.topic, str):
                                self.client.subscribe(self.topic, self.qos)
                                if self.logger is not None:
                                    self.logger.info("Resubscribed to topic: %s" % self.topic)
                            else:
                                if self.logger is not None:
                                    self.logger.warning("No valid topic(s) to resubscribe.")
                            break
                        except Exception as sub_all_e:
                            if self.logger is not None:
                                self.logger.error("Subscription error: %s" % str(sub_all_e))
                            self.client.close()
                            if self.__status_cb:
                                self.__status_cb(self.FAILED)
                            utime.sleep(5)
                            continue
                    else:
                        if self.logger is not None:
                            self.logger.warning("Data call inactive. Waiting...")
                        utime.sleep(10)
                else:
                    if self.logger is not None:
                        self.logger.warning("Network not registered. Waiting...")
                    utime.sleep(5)

        except Exception as general_e:
            if self.logger is not None:
                self.logger.error("Unexpected error in reconnect(): %s" % str(general_e))
            if self.__status_cb:
                self.__status_cb(self.FAILED)
        finally:
            if self.mp_lock.locked():
                self.mp_lock.release()
            if self.logger is not None:
                self.logger.info("Reconnection attempt complete.")
        return True


    def nw_cb(self, args):
        '''
        Call the callback function of data call.
        '''
        nw_sta = args[1]
        if nw_sta == 1:
            # Network connected.
            if self.logger is not None:
                self.logger.info("*** network connected! ***")
            self.__nw_flag = True
        else:
            # Network disconnected.
            if self.logger is not None:
                self.logger.info("*** network not connected! ***")
            self.__nw_flag = False

    def __listen(self):
        """
        Listen for incoming MQTT messages in a loop.

        This method blocks and waits for messages using client.wait_msg(). It runs continuously
        until TaskEnable is False. If a network or MQTT socket error occurs, it handles the
        reconnection logic accordingly.

        Returns:
            -1: if an unrecoverable error occurs and the loop exits early.
        """
        while True:
            try:
                if not TaskEnable:
                    break
                self.client.wait_msg()
            except OSError as e:
                # Determine whether the network is disconnected.
                if self.logger:
                    self.logger.warning("OS error occured: {}".format(e))
                if not self.__nw_flag:
                    # Reconnect after the network is restored from disconnection.
                    self.reconnect()
                # Reconnect when the socket status is abnormal.
                elif self.client.get_mqttsta() != 0 and TaskEnable:
                    self.reconnect()
                else:
                    # If no valid recovery condition, exit with error
                    return -1

    def loop_forever(self):
        global TaskEnable
        TaskEnable = True

        task_stacksize =_thread.stack_size()
        name,platform = uos.uname()[1].split("=",1)
        if platform == "EC600E" or platform == "EC800E":
            _thread.stack_size(8 * 1024)
        elif platform == "FCM362K":
            _thread.stack_size(3 * 1024)
        else:
            _thread.stack_size(16 * 1024)
        # Before creating a thread, modify the thread stack space according to the platform.
        _thread.start_new_thread(self.__listen, ())
        # After the thread is created successfully, the platform thread stack default size is restored.
        _thread.stack_size(task_stacksize)
