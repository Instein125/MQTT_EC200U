'''
File: button_service.py
Created Date: Tuesday June 17th 2025
Author: Samman Shrestha
Last Modified: We/06/2025 11:47:05
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

from usr.extensions.my_button import Button
from usr.config import Config

cfg = Config.BUTTON


class ButtonService:
    def __init__(self, cb_up=None, cb_down=None,
                 cb_up_release=None, cb_down_release=None,
                 cb_up_long=None, cb_down_long=None):

        up_pin = cfg["up_pin"]
        down_pin = cfg["down_pin"]
        debounce_ms = cfg["debounce_ms"]
        long_press_ms = cfg["long_press_ms"]

        self.button_up = Button(
            pin=up_pin,
            cb_press=cb_up,
            cb_release=cb_up_release,
            cb_long_press=cb_up_long,
            ms_debounce=debounce_ms,
            ms_long_press=long_press_ms
        )

        self.button_down = Button(
            pin=down_pin,
            cb_press=cb_down,
            cb_release=cb_down_release,
            cb_long_press=cb_down_long,
            ms_debounce=debounce_ms,
            ms_long_press=long_press_ms
        )
