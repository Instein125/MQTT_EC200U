'''
File: my_netmanager.py
Created Date: Tuesday June 10th 2025
Author: Samman Shrestha
Last Modified: Tu/06/2025 02:22:42
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''
import sys
import net
import sim
import osTimer
import _thread
import dataCall
import checkNet
import utime as time
import log

# Application version
APP_VERSION = "1.0.0"


def get_version():
    return APP_VERSION


class MyNetManager:
    """This class is for net management."""

    def __init__(self):
        self.__conn_flag = 0
        self.__disconn_flag = 0
        self.__reconn_flag = 0
        self.__callback = None
        self.__net_check_timer = osTimer()             # Timer to periodically check and maintain network connection
        self.__net_check_cycle = 5 * 60 * 1000         # Interval for network check: 5 minutes (in milliseconds)        
        self.__reconn_tid = None                       # Thread ID for the current reconnection thread (if running)

        self.logger = None
        
        dataCall.setCallback(self.__net_callback)

    def setLogger(self, level):
        """
        Set up logging configuration
        Args:
            log level (str): log level.
        """
        self.logger = log.getLogger(self.__class__.__name__)
        self.logger.setLevel(level)

    def __net_callback(self, args):
        if self.logger is not None:
            self.logger.debug("profile id[%s], net state[%s], last args[%s]" % args)
        # 0 means the network is disconnected and 1 means the network is connected 
        if args[1] == 0:
            if self.logger is not None:
                self.logger.debug("NETWORK DISCONNECTED")
            self.__net_check_timer.stop()
            self.net_check(None)
            self.__net_check_timer.start(self.__net_check_cycle, 1, self.net_check)
        if callable(self.__callback):
            self.__callback(args)

    def set_callback(self, callback):
        if callable(callback):
            self.__callback = callback
            return True
        return False
    
    def net_connect(self):
        """
        Attempt to establish a cellular network connection.

        This method performs the following steps:
        1. Prevents concurrent connection attempts.
        2. Ensures the modem is in full functionality mode.
        3. Verifies that the SIM card is ready.
        4. Waits for the network to be registered and ready.
        5. Starts a periodic timer to monitor network status.

        Returns:
            int:
                0   - Connection successful.
            -1   - General failure.
            -2   - Connection already in progress.
            -3   - Failed to enable modem function.
            -4   - SIM card not ready.
            -5   - Network registration failed.
        """
        res = -1  # Default to general failure

        # Prevent concurrent connection attempts
        if self.__conn_flag != 0:
            return -2
        self.__conn_flag = 1

        try:
            # Ensure modem is in full functionality mode
            if net.getModemFun() != 1:
                _res = self.net_disconnect()
                if self.logger is not None:
                    self.logger.debug("net_connect net_disconnect %s" % _res)
                time.sleep(5)  # Wait for modem to settle
                # set modem work mode to full functionality
                _res = net.setModemFun(1)
                if self.logger is not None:
                    self.logger.debug("net.setModemFun(1) %s" % _res)
                if _res != 0:
                    return -3  # Failed to set modem function

            # Check SIM card readiness
            if self.sim_status() != 1:
                if self.logger is not None:
                    self.logger.error("SIM card is not ready.")
                return -4  # SIM not ready

            # Wait for network registration and readiness (timeout: 300 seconds)
            _res = checkNet.waitNetworkReady(300)
            if self.logger is not None:
                self.logger.debug("checkNet.waitNetworkReady %s" % str(_res))
            res = 0 if _res == (3, 1) else -5  # (3, 1) indicates success

        except Exception as e:
            # Log and print any exceptions encountered
            if self.logger is not None:
                self.logger.error(str(e))

        finally:
            # Clear the connection flag regardless of outcome
            self.__conn_flag = 0

        # Restart periodic network status checker (every 5 minutes)
        self.__net_check_timer.stop()
        self.__net_check_timer.start(self.__net_check_cycle, 1, self.net_check)

        return res

    def net_disconnect(self):
        """
        Disconnects the device from the cellular network.

        This function:
        1. Ensures only one disconnection process runs at a time using a flag.
        2. Tries to disable the modem by setting it to either:
        - Disable UE from both transmitting and receiving RF signals. (value 4), or
        - Minimum functionality mode (value 0).
        3. Stops the periodic network check timer.
        
        Returns:
            bool: True if disconnection succeeded, False otherwise.
        """
        # Prevent concurrent disconnection attempts
        if self.__disconn_flag != 0:
            return False
        self.__disconn_flag = 1

        # Attempt to set modem to flight mode (4); if it fails, try minimum functionality mode (0)
        res = True if (net.setModemFun(4) == 0) else (net.setModemFun(0) == 0)

        # Stop network monitoring timer since the device is now disconnected
        self.__net_check_timer.stop()

        # Clear the disconnection flag
        self.__disconn_flag = 0

        return res
    
    def net_reconnect(self):
        """
        Reconnects the device to the cellular network.

        This function:
        1. Prevents concurrent reconnection attempts using a flag.
        2. Disconnects the current network connection.
        3. Attempts to reconnect by calling net_connect().
        4. Resets internal flags and thread ID after completion.

        Returns:
            bool: True if reconnection succeeded, False otherwise.
        """
        # Avoid parallel reconnection attempts
        if self.__reconn_flag != 0:
            return False
        self.__reconn_flag = 1

        # Disconnect from current network, then try reconnecting
        res = self.net_connect() if self.net_disconnect() else False

        # Clear reconnection flag and thread ID
        self.__reconn_flag = 0
        self.__reconn_tid = None

        return res
    
    def net_status(self):
        """
        Check overall network status.

        Determines whether the device is fully connected by verifying:
        1. SIM card is ready.
        2. Modem is registered to the network.
        3. A data call is active.

        Returns:
            bool: True if all conditions are met, False otherwise.
        """
        return True if self.sim_status() == 1 and self.net_state() and self.call_state() else False

    def net_state(self):
        """
        Check whether the modem is registered to the network.

        The modem is considered registered if the registration state
        is either:
            - 1: Registered to home network
            - 5: Registered while roaming

        Returns:
            bool: True if the modem is registered to a network, False otherwise.
        """
        try:
            _net_state_ = net.getState()
            if self.logger is not None:
                self.logger.debug("net.getState() %s" % str(_net_state_))

            # Check if returned value is a valid tuple with sufficient length
            # and if the registration state is 1 (home) or 5 (roaming)
            return (
                isinstance(_net_state_, tuple) and
                len(_net_state_) >= 2 and
                _net_state_[1][0] in (1, 5)
            )
        except Exception as e:
            # Log and print any exceptions that occur
            if self.logger is not None:
                self.logger.error(str(e))

        # Return False if an exception occurred or registration is invalid
        return False

    def net_config(self, state=None):
        """
        Get or set the network configuration of the modem.

        Args:
            state (int or None): The configuration state to set.
                - None: Return the current network configuration.
                - 0: GSM mode
                - 5: LTE mode
                - 6: GSM_LTE automatic mode
                - 8: GSM_LTE (LTE prefered) mode
        
        Returns:
            object | bool:
                - If state is None: returns current configuration from net.getConfig().
                - If state is 0, 5, 6 or 8: returns True if successfully set, else False.
                - For other values: returns False.
        """
        if state is None:
            # Return current network configuration
            return net.getConfig()
        elif state in (0, 5, 6, 8):
            # Attempt to set new configuration state
            return (net.setConfig(state) == 0)
        
        # Invalid state provided
        if self.logger is not None:
            self.logger.error("Invalid state provided")
        return False

    def net_mode(self):
        """
        Determine the current network access mode based on the RAT (Radio Access Technology) code.

        Returns:
            int:
                - 2: 2G (GSM, EGPRS)
                - 3: 3G (UTRAN/HSPA/HSPA+)
                - 4: 4G (LTE, LTE-CA)
                - -1: Unknown, invalid, or unsupported mode
        """
        _net_mode_ = net.getNetMode()

        # Validate the result
        if _net_mode_ == -1 or not isinstance(_net_mode_, tuple) or len(_net_mode_) < 4:
            return -1  # Error or unexpected format

        rat = _net_mode_[3]  # Access technology (ACT) mode

        if rat in (0, 1, 3):  # GSM, Compact, GSM w/EGPRS
            return 2
        elif rat in (2, 4, 5, 6, 8):  # UTRAN, HSPA, HSPA+
            return 3
        elif rat in (7, 9):  # LTE, LTE with Carrier Aggregation
            return 4

        return -1  # Unknown ACT value
    
    def net_check(self, args):
        """
        Check the network status and attempt to reconnect if disconnected.

        Behavior:
            - Checks if the network is currently connected.
            - If not connected, it starts a new thread to perform a network reconnect.
            - Ensures only one reconnect thread runs at a time.
            - Handles exceptions by logging the error and printing the stack trace.
        """
        # If network is not connected
        print()
        if not self.net_status():
            try:
                # Check if reconnect thread is not running or does not exist
                if not self.__reconn_tid or (self.__reconn_tid and not _thread.threadIsRunning(self.__reconn_tid)):
                    _thread.stack_size(0x2000)  # Set thread stack size
                    # Start a new thread to reconnect network and save its thread ID
                    self.__reconn_tid = _thread.start_new_thread(self.net_reconnect, ())
            except Exception as e:
                if self.logger is not None:
                    self.logger.error(str(e))

    def call_state(self):
        """
        Check if the data call (network connection) is currently active.

        Returns:
            bool: True if the data call is active, False otherwise.
        """
        try:
            call_info = self.call_info()  # Get current data call information
            if self.logger is not None:
                self.logger.debug("dataCall.getInfo %s" % str(call_info))

            # Check if call_info is a tuple with at least 3 elements
            # and that the third element's first item equals 1 (active)
            if isinstance(call_info, tuple) and len(call_info) >= 3 and call_info[2][0] == 1:
                return True
            else:
                return False
        except Exception as e:
            if self.logger is not None:
                self.logger.error(str(e))
        return False

    def call_info(self):
        """
        Retrieve the current data call information.

        Returns:
            -1: for failed execution
            tuple: (profileID, ipType, [state, reconnect, addr, priDNS, secDNS]).
        """
        return dataCall.getInfo(1, 0)

    def sim_status(self):
        """
        Check the SIM card status with retries.

        Returns:
            int: SIM status code.
                1 means SIM is ready.
                -1 means SIM status is unknown (not ready yet).
                Other values indicate different SIM states.
        """
        count = 0
        # Retry up to 3 times if SIM status is unknown (-1)
        while sim.getStatus() == -1 and count < 3:
            time.sleep_ms(100)  # wait 100ms before retry
            count += 1
        # Return the final SIM status after retrying
        return sim.getStatus()
    
    def sim_imsi(self):
        """Get the SIM IMSI (International Mobile Subscriber Identity)."""
        return sim.getImsi()

    def sim_iccid(self):
        """Get the SIM ICCID (Integrated Circuit Card Identifier)."""
        return sim.getIccid()

    def signal_csq(self):
        """Query the signal strength (CSQ). Returns RSSI value (0-31)."""
        return net.csqQueryPoll()

    def signal_level(self):
        """
        Calculate signal level on a scale of 0 to 5 based on RSSI.

        Returns:
            int: Signal level from 0 (no signal) to 5 (strongest).
        """
        signal = self.signal_csq()
        # Convert raw RSSI (0-31) to level (0-5), or 0 if out of range
        _signal_level_ = int(signal * 5 / 31) if 0 <= signal <= 31 else 0
        return _signal_level_



