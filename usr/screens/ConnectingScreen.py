'''
File: ConnnectinScreen.py
Created Date: Monday June 9th 2025
Author: Prashant Bhandari
Last Modified: We/06/2025 11:46:59
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

from usr.screens.screen import Screen
import usr.Eventstore as Eventstore
import usr.services.time_service as time_service
from usr.config import Config

asset_cfg = Config.ASSETS

class ConnectingScreen(Screen):
    def __init__(self):
        self.screen = None  # Initialize screen attribute
        self.name = 'ConnectingScreen'
        
    def create(self):  
        # Create the screen object and store it as instance variable
        self.screen = self.lv.obj()

        self.screen.set_size(self.height, self.width)
        self.screen.set_scrollbar_mode(self.lv.SCROLLBAR_MODE.OFF)
        
        # Set style for ConnectingScreen, Part: lv.PART.MAIN, State: lv.STATE.DEFAULT.
        self.screen.set_style_bg_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_color(self.lv.color_hex(0x000000), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_grad_dir(self.lv.GRAD_DIR.NONE, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)

        self.ConnectingScreen_ConnectingSpinner = None
        self.show_spinner()

        # Create ConnectingScreen_ImgSignal
        self.ConnectingScreen_ImgSignal = self.lv.img(self.screen)
        self.ConnectingScreen_ImgSignal.set_src(asset_cfg["img_no_signal"])
        self.ConnectingScreen_ImgSignal.add_flag(self.lv.obj.FLAG.CLICKABLE)
        self.ConnectingScreen_ImgSignal.set_pivot(50,50)
        self.ConnectingScreen_ImgSignal.set_angle(0)
        self.ConnectingScreen_ImgSignal.set_pos(4, 4)
        self.ConnectingScreen_ImgSignal.set_size(20, 14)
        # Set style for ConnectingScreen_ImgSignal, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        self.ConnectingScreen_ImgSignal.set_style_img_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ImgSignal.set_style_radius(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ImgSignal.set_style_clip_corner(True, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)

        # Create ConnectingScreen_BatteryPercent
        ConnectingScreen_BatteryPercent = self.lv.label(self.screen)
        ConnectingScreen_BatteryPercent.set_text("80%")
        ConnectingScreen_BatteryPercent.set_long_mode(self.lv.label.LONG.WRAP)
        ConnectingScreen_BatteryPercent.set_width(self.lv.pct(100))
        ConnectingScreen_BatteryPercent.set_pos(217, 4)
        ConnectingScreen_BatteryPercent.set_size(100, 16)
        # Set style for ConnectingScreen_BatteryPercent, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        ConnectingScreen_BatteryPercent.set_style_border_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_radius(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_color(self.lv.color_hex(0xffffff), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_font(self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_letter_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_line_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_text_align(self.lv.TEXT_ALIGN.RIGHT, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_bg_opa(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_pad_top(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_pad_right(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_pad_bottom(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_pad_left(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        ConnectingScreen_BatteryPercent.set_style_shadow_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)

        # Create ConnectingScreen_Time
        self.ConnectingScreen_Time = self.lv.label(self.screen)
        self.ConnectingScreen_Time.set_text(time_service.get_time() + "\n")
        self.ConnectingScreen_Time.set_long_mode(self.lv.label.LONG.WRAP)
        self.ConnectingScreen_Time.set_width(self.lv.pct(100))
        self.ConnectingScreen_Time.set_pos(110, 4)
        self.ConnectingScreen_Time.set_size(100, 16)
        # Set style for self.ConnectingScreen_Time, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        self.ConnectingScreen_Time.set_style_border_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_radius(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_color(self.lv.color_hex(0xffffff), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_font(self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_letter_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_line_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_text_align(self.lv.TEXT_ALIGN.CENTER, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_bg_opa(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_pad_top(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_pad_right(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_pad_bottom(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_pad_left(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_Time.set_style_shadow_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)

        # Create self.ConnectingScreen_ConnectingText
        self.ConnectingScreen_ConnectingText = self.lv.label(self.screen)
        self.ConnectingScreen_ConnectingText.set_text("Connecting...")
        self.ConnectingScreen_ConnectingText.set_long_mode(self.lv.label.LONG.SCROLL_CIRCULAR)
        self.ConnectingScreen_ConnectingText.set_width(self.lv.pct(100))
        self.ConnectingScreen_ConnectingText.set_pos(82, 184)
        self.ConnectingScreen_ConnectingText.set_size(160, 32)
        # Set style for self.ConnectingScreen_ConnectingText, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        self.ConnectingScreen_ConnectingText.set_style_border_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_radius(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_color(self.lv.color_hex(0xffffff), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_font(self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_letter_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_line_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_text_align(self.lv.TEXT_ALIGN.CENTER, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_bg_opa(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_pad_top(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_pad_right(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_pad_bottom(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_pad_left(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.ConnectingScreen_ConnectingText.set_style_shadow_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.screen.update_layout()

        Eventstore.subscribe("time.update", self.__update_time_cb, owner=self)
        Eventstore.subscribe("network.status", self.__status_network_signal_cb, owner=self)

    def destroy(self):
        self.active = False
        Eventstore.unsubscribe_by_owner(self)  # Clean up all subscriptions

    def show_spinner(self):
        if self.ConnectingScreen_ConnectingSpinner is None:
            # Create ConnectingScreen_ConnectingSpinner
            self.ConnectingScreen_ConnectingSpinner = self.lv.spinner(self.screen, 1000, 60)
            self.ConnectingScreen_ConnectingSpinner.set_pos(129, 92)
            self.ConnectingScreen_ConnectingSpinner.set_size(66, 72)
            # Set style for self.ConnectingScreen_ConnectingSpinner, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
            self.ConnectingScreen_ConnectingSpinner.set_style_pad_top(5, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_pad_bottom(5, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_pad_left(5, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_pad_right(5, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_bg_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_bg_color(self.lv.color_hex(0x000000), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_bg_grad_dir(self.lv.GRAD_DIR.NONE, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_width(12, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_color(self.lv.color_hex(0xd5d6de), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_shadow_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
            # Set style for self.ConnectingScreen_ConnectingSpinner, Part: self.lv.PART.INDICATOR, State: self.lv.STATE.DEFAULT.
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_width(12, self.lv.PART.INDICATOR|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_opa(255, self.lv.PART.INDICATOR|self.lv.STATE.DEFAULT)
            self.ConnectingScreen_ConnectingSpinner.set_style_arc_color(self.lv.color_hex(0x2195f6), self.lv.PART.INDICATOR|self.lv.STATE.DEFAULT)

    def hide_spinner(self):
        if self.ConnectingScreen_ConnectingSpinner:
            self.ConnectingScreen_ConnectingSpinner.delete()
            self.ConnectingScreen_ConnectingSpinner = None
    
    def __update_time_cb(self, event, time_str):
        """
        Update the time shown on the ConnectingScreen_Time label.

        Args:
            time_str (str): The current time as a string (e.g., "11:45:01")
        """
        self.ConnectingScreen_Time.set_text(time_str + "\n")

    def __status_network_signal_cb(self, event, msg):
        if msg == "CONNECTED":
            self.ConnectingScreen_ImgSignal.set_src(asset_cfg["img_signal"])
            self.ConnectingScreen_ConnectingText.set_text("Connected")
            self.hide_spinner()

        elif msg == "DISCONNECTED":
            self.ConnectingScreen_ImgSignal.set_src(asset_cfg["img_no_signal"])
            self.ConnectingScreen_ConnectingText.set_text("Connecting")
            self.show_spinner()

        else:
            print("UNKNOWN MESSAGE")

        self.screen.update_layout()
        

