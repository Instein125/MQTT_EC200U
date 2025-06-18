'''
File: config.py
Created Date: Wednesday June 18th 2025
Author: Samman Shrestha
Last Modified: We/06/2025 12:12:07
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

'''
Note: change name to config.py if same file is used in application
'''
from machine import Pin
import lvgl as lv
from misc import ADC

class Config:
    # MQTT Configuration
    MQTT = {
        "server": "server.url",
        "port": 18333,
        "client_id": "MY_EC200U",
        "username": "username",
        "password": "password",
        "ssl_cert": "path/to/mqtt_ca.crt",
        "subscribe_topic": "test/message"
    }

    # Button Configuration
    BUTTON = {
        "up_pin": Pin.GPIO10,
        "down_pin": Pin.GPIO12,
        "debounce_ms": 50,
        "long_press_ms": 1000
    }

    # Display configuration
    DISPLAY = {
        "width": 240,
        "height": 320,
        "clk": 52000,
        "backlight_pin": Pin.GPIO28,
        "rotation":lv.DISP_ROT._90
    }

    # Asset paths
    ASSETS = {
        "img_no_signal": "U:/noSignal.png",
        "img_signal": "U:/Signal.png",
        "img_4g": "U:/4g.png"
    }

    # Battery Configuration
    BATTERY = {
        # adc_args: (adc_num, adc_period, factor)
        "adc_args": (ADC.ADC1, 25, 3540/717),
        "chrg_gpion": Pin.GPIO30,    
        # Note: Both stdby_gpion and pgood_gpion cant be used together           
        "pgood_gpion": Pin.GPIO29,             
        "battery_ocv": "YT-LION-PINK-2600",
        "use_batt_ic": False
    }

    # Scroll Configuration
    SCROLL = {
        "base_scroll": 20, # Initial scroll step
        "max_scroll": 80, # Maximum scroll step
        "scroll_increment": 10, # How much to increase per step
        "step_interval": 500, # ms after which speed increases
        "scroll_interval": 50 # Initial delay between scrolls (ms)
    }


