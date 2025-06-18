'''
File: my_button.py
Created Date: Thursday June 5th 2025
Author: Samman Shrestha
Last Modified:
Modified By:
Copyright (c) 2025 YARSA TECH
'''

import machine
from machine import ExtInt
import time


class Button:
    """
    A class to handle GPIO button inputs with debouncing, long-press detection,
    and state tracking.

    Attributes:
        pin (int): GPIO pin number.
        cb_press (function): User-defined callback function for button pressed.
        cb_release (function): User-defined callback function for button released.
        cb_long_press (function): User-defined callback function for button long pressed.
        ms_debounce (int): Debounce time in milliseconds.
        ms_long_press (int): Long press duration threshold in milliseconds.
        timer (machine.Timer): timer object.
    """

    def __init__(self,
                 pin,
                 cb_press=None,
                 cb_release = None,
                 cb_long_press = None,
                 ms_debounce=50,
                 ms_long_press=1000,
                 timer=None):
        self.pin_num = pin
        self.cb_user_press = cb_press
        self.cb_user_release = cb_release
        self.cb_user_long_press = cb_long_press
        self.ms_debounce = ms_debounce
        self.ms_long_press = ms_long_press
        # Default to Timer 0 if not provided
        self.timer = timer or machine.Timer(0)

        self.extint = ExtInt(self.pin_num, 
                             ExtInt.IRQ_RISING_FALLING,
                             ExtInt.PULL_PU, 
                             self._irq_handler)
        self.extint.enable()

        self._state_last = self.extint.read_level()
        self._time_last_debounce = 0
        self._press_time = None
        self._reported_long_press = False

        

    def _irq_handler(self, args):
        time_current = time.ticks_ms()
        state_current = self.extint.read_level()

        # Debounce logic
        if state_current == self._state_last:
            self._time_last_debounce = time_current
            if (time.ticks_diff(time_current, self._time_last_debounce) < self.ms_debounce):
                return
                
        time_current = time.ticks_ms()

        # button pressed
        if state_current == 0:
            self._handle_press()
        # button released
        else:
            self._handle_release()

        self._state_last = state_current

    def _handle_press(self):
        self._press_time = time.ticks_ms()
        self._reported_long_press = False
        self.timer.start(period=self.ms_long_press, mode=machine.Timer.ONE_SHOT,
                         callback=self._long_press_handler)
        if self.cb_user_press:
            self.cb_user_press()

    def _handle_release(self):
        self.timer.stop()
        if self.cb_user_release:
            self.cb_user_release()
        self._press_time = None
        self._reported_long_press = False

    def _long_press_handler(self, timer):
        if self.extint.read_level() == 0:
            self._reported_long_press = True
            if self.cb_user_long_press:
                self.cb_user_long_press()
