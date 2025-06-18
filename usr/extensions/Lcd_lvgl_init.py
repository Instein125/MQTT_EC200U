'''
File: Lcd_lvgl_init.py
Created Date: Thursday June 5th 2025
Author: Samman Shrestha
Last Modified: Fr/06/2025 04:19:37
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

from machine import LCD, Pin
import lvgl as lv

# ----------------------------
# Default LCD Initialization Commands
# ----------------------------

# Initialization commands for the LCD
INIT_PARAMS = (
    0, 0, 0x11,
    2, 0, 120,
    0, 0, 0x00,
    0, 1, 0x36,
    1, 1, 0x00,
    0, 1, 0x3A,
    1, 1, 0x05,
    0, 1, 0x35,
    1, 1, 0x00,
    0, 1, 0xC7,
    1, 1, 0x00,
    0, 1, 0xCC,
    1, 1, 0x09,
    0, 5, 0xB2,
    1, 1, 0x0C,
    1, 1, 0x0C,
    1, 1, 0x00,
    1, 1, 0x33,
    1, 1, 0x33,
    0, 1, 0xB7,
    1, 1, 0x35,
    0, 1, 0xBB,
    1, 1, 0x36,
    0, 1, 0xC0,
    1, 1, 0x2C,
    0, 1, 0xC2,
    1, 1, 0x01,
    0, 1, 0xC3,
    1, 1, 0x0D,
    0, 1, 0xC4,
    1, 1, 0x20,
    0, 1, 0xC6,
    1, 1, 0x0F,
    0, 2, 0xD0,
    1, 1, 0xA4,
    1, 1, 0xA1,
    0, 14, 0xE0,
    1, 1, 0xD0,
    1, 1, 0x17,
    1, 1, 0x19,
    1, 1, 0x04,
    1, 1, 0x03,
    1, 1, 0x04,
    1, 1, 0x32,
    1, 1, 0x41,
    1, 1, 0x43,
    1, 1, 0x09,
    1, 1, 0x14,
    1, 1, 0x12,
    1, 1, 0x33,
    1, 1, 0x2C,
    0, 14, 0xE1,
    1, 1, 0xD0,
    1, 1, 0x18,
    1, 1, 0x17,
    1, 1, 0x04,
    1, 1, 0x03,
    1, 1, 0x04,
    1, 1, 0x31,
    1, 1, 0x46,
    1, 1, 0x43,
    1, 1, 0x09,
    1, 1, 0x14,
    1, 1, 0x13,
    1, 1, 0x31,
    1, 1, 0x2D,
    0, 0, 0x29,
    0, 1, 0x36,
    1, 1, 0x00,
    0, 0, 0x2c,
)
INIT_DATA = bytearray(INIT_PARAMS)

# Commands that should not be run during normal init
INVALID_DATA = bytearray((
    0, 4, 0x2a,
    1, 1, 0xf0,
    1, 1, 0xf1,
    1, 1, 0xe0,
    1, 1, 0xe1,
    0, 4, 0x2b,
    1, 1, 0xf2,
    1, 1, 0xf3,
    1, 1, 0xe2,
    1, 1, 0xe3,
    0, 0, 0x2c,
))

# Commands to turn the display off
DISPLAY_OFF = bytearray((0, 0, 0x28, 2, 0, 120, 0, 0, 0x10))

# Commands to turn the display on
DISPLAY_ON = bytearray((0, 0, 0x11, 2, 0, 20, 0, 0, 0x29))

backlight_pin = None

def init_display(
    width=240,
    height=320,
    clk=52000,
    backlight_pin=Pin.GPIO28,
    rotation=lv.DISP_ROT._90
):
    """
    Initializes the LCD and sets up the LVGL display driver.

    Parameters:
        width (int): Horizontal resolution of the display in pixels.
        height (int): Vertical resolution of the display in pixels.
        clk (int): Clock speed for the LCD interface.
        backlight_pin (int): GPIO pin used to control LCD backlight.
        rotation (lv.DISP_ROT): LVGL rotation enum. Use lv.DISP_ROT._0, _90, _180, _270.

    Returns:
        lv (module): The initialized LVGL module ready for use.
    """

    # ----------------------------
    # Init LCD Backlight
    # ----------------------------
    init_backlight_pin(backlight_pin)
    turnOff_Backlight()

    # ----------------------------
    # Initialize LCD Panel
    # ----------------------------
    lcd = LCD()

    
    lcd.lcd_init(
        INIT_DATA,
        width,
        height,
        clk,
        1,  
        4,      
        0,      
        INVALID_DATA,
        DISPLAY_ON,
        DISPLAY_OFF,
        None 
    )

    # ----------------------------
    # Initialize LVGL
    # ----------------------------
    lv.init()

    # Create draw buffer
    disp_buf = lv.disp_draw_buf_t()
    buf1 = bytearray(width * height * 2)
    disp_buf.init(buf1, None, len(buf1))

    # Register display driver
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf
    disp_drv.flush_cb = lcd.lcd_write
    disp_drv.hor_res = width
    disp_drv.ver_res = height
    disp_drv.sw_rotate = 1
    disp_drv.rotated = rotation
    disp_drv.register()

    print("LVGL display initialized with resolution {}x{}".format(width, height))
    return lv

def init_backlight_pin(gpion):
    global backlight_pin
    backlight_pin = Pin(gpion, Pin.OUT)

def turnOn_Backlight():
    backlight_pin.write(1)

def turnOff_Backlight():
    backlight_pin.write(0)
