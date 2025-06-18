'''
File: ui.py
Created Date: Thursday June 12th 2025
Author: Samman Shrestha
Last Modified: We/06/2025 11:46:14
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

# from usr.extensions.Lcd_lvgl_init import init_display
# from usr.screens.screen import Screen
# import lvgl
# from machine import Pin
# from usr import Eventstore
# import utime

from usr.extensions.Lcd_lvgl_init import init_display, turnOn_Backlight
from usr.screens.screen import Screen
import lvgl
from machine import Pin
import usr.Eventstore as Eventstore
import utime
from usr.config import Config

cfg = Config.DISPLAY

class Ui():
    def __init__(self):
        # LCD Configuration
        self.LCD_SIZE_W = cfg["width"]
        self.LCD_SIZE_H = cfg["height"]
        self.LCD_ROTATION = cfg["rotation"]
        self.LCD_BCK_PIN = cfg["backlight_pin"]
        self.LCD_CLK = cfg["clk"]

        # LVGL and display objects
        self.lv = None
        self.COLOR_SIZE = None
        self.COLOR_IS_SWAPPED = None

        self.screens = []

        # Initialize the display and screens
        self.__lcd_init()


    def __lcd_init(self):
        """Initialize LCD display and LVGL"""
        self.lv = init_display(
            width=self.LCD_SIZE_W,
            height=self.LCD_SIZE_H,
            backlight_pin=self.LCD_BCK_PIN,
            rotation=self.LCD_ROTATION,
            clk=self.LCD_CLK
        )
        
        self.COLOR_SIZE = self.lv.color_t.__SIZE__
        self.COLOR_IS_SWAPPED = hasattr(self.lv.color_t().ch, 'green_h')

        # Configure the base Screen class with display settings
        Screen.set_display_config(self.lv, self.LCD_SIZE_W, self.LCD_SIZE_H)
        
        # Start lvgl
        self.lv.tick_inc(5)
        self.lv.task_handler()
        
        print("LCD init complete")

    def __load_screen(self, event, screen_name):
        """
        Load a specific screen
        Args:
            screen_name: Name of the screen to load
        """
        for screen in self.screens:
            if screen.name == screen_name:
                self.lv.scr_load(screen.screen)

    def __create(self):
        for screen in self.screens:
            screen.create()

    def __destroy_screen(self, event, screen_name):
        """
        destroys the screen instance
        Args:
            screen_name: Name of the screen to load
        """
        for screen in self.screens:
            if screen.name == screen_name:
                screen.destroy()

    def add_screen(self, screen_instance):
        """
        Add screen to GUI
        Args:
            screen_instance: Screen object instance
        """
        if isinstance(screen_instance, Screen):
            self.screens.append(screen_instance)
        return self
    
    def start(self):
        """
        Startup of GUI
        """
        self.__create()
        Eventstore.subscribe("load_screen", self.__load_screen)
        Eventstore.subscribe("destroy_screen", self.__destroy_screen)

        Eventstore.publish("load_screen", "WelcomeScreen")
        turnOn_Backlight()
        
        utime.sleep(2)
        Eventstore.publish("destroy_screen", "WelcomeScreen")
        Eventstore.publish("load_screen", "ConnectingScreen")
        

    
    