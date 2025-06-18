'''
File: screen.py
Created Date: Thursday June 12th 2025
Author: Samman Shrestha
Last Modified: Th/06/2025 04:56:19
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

class Screen:
    """Base class for all screens"""
    
    # Class variables to be shared across all screen instances
    lv = None
    width = None
    height = None
    
    @classmethod
    def set_display_config(cls, lv, width, height):
        """
        Set the display configuration for all screens
        This should be called once from the UI class
        """
        cls.lv = lv
        cls.width = width
        cls.height = height