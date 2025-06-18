'''
File: WelcomeScreen.py
Created Date: Monday June 9th 2025
Author: Prashant Bhandari
Last Modified: Fr/06/2025 04:00:50
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''
from usr.screens.screen import Screen
import usr.Eventstore as Eventstore

class WelcomeScreen(Screen):
    def __init__(self):
        self.screen = None  # Initialize screen attribute
        self.name = 'WelcomeScreen'
        self.active = True
       
    def create(self):
        # Create the screen object and store it as instance variable
        self.screen = self.lv.obj()
        
        self.screen.set_size(self.height, self.width)
        self.screen.set_scrollbar_mode(self.lv.SCROLLBAR_MODE.OFF)
        
        # Set style for WelcomeScreen, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        self.screen.set_style_bg_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_color(self.lv.color_hex(0x000000), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_grad_dir(self.lv.GRAD_DIR.NONE, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        
        # Create WelcomeScreen_label_1
        WelcomeScreen_label_1 = self.lv.label(self.screen)
        WelcomeScreen_label_1.set_text("Welcome Screen")
        WelcomeScreen_label_1.set_long_mode(self.lv.label.LONG.SCROLL_CIRCULAR)
        WelcomeScreen_label_1.set_width(self.lv.pct(100))
        WelcomeScreen_label_1.set_pos(80, 104)
        # WelcomeScreen_label_1.set_pos(0, 0)
        WelcomeScreen_label_1.set_size(160, 32)
        
        # Set style for WelcomeScreen_label_1, Part: self.lv.PART.MAIN, State: self.lv.STATE.DEFAULT.
        WelcomeScreen_label_1.set_style_border_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_radius(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_color(self.lv.color_hex(0xffffff), self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_font(self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_opa(255, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_letter_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_line_space(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_text_align(self.lv.TEXT_ALIGN.CENTER, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_bg_opa(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_pad_top(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_pad_right(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_pad_bottom(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_pad_left(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        WelcomeScreen_label_1.set_style_shadow_width(0, self.lv.PART.MAIN|self.lv.STATE.DEFAULT)
        
        self.screen.update_layout()

    def destroy(self):
        self.active = False
        Eventstore.unsubscribe_by_owner(self)  # Clean up all subscriptions