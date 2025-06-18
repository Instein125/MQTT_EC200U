'''
File: time_service.py
Created Date: Friday June 13th 2025
Author: Samman Shrestha
Last Modified: Fr/06/2025 12:02:15
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''
import utime
import _thread
import usr.Eventstore as Eventstore

_current_time = "00:00:00"  # Default time

def set_time(time_str):
    """
    Set the global shared time.
    
    Args:
        time_str (str): The time string to set (e.g., "11:45:01")
    """
    global _current_time
    _current_time = time_str

def get_time():
    """
    Get the current shared time.
    
    Returns:
        str: The currently set time string.
    """
    return _current_time

def get_current_time_str():
    now = utime.localtime()  # returns tuple: (yearW, month, mday, hour, minute, second, weekday, yearday)
    hour = now[3]
    minute = now[4]
    second = now[5]
    # Format manually (no f-strings if not allowed)
    return "%02d:%02d:%02d" % (hour, minute, second)

def run_time_updater():
    def loop():
        while True:
            
            set_time(get_current_time_str())
            Eventstore.publish_async("time.update", get_time())
            utime.sleep(1)

    _thread.start_new_thread(loop, ())