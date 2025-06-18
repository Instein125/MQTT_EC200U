'''
File: my_battery.py
Created Date: Thursday June 5th 2025
Author: Samman Shrestha
Last Modified: Tu/06/2025 12:53:08
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

import utime
from misc import Power, ADC
import log
from machine import Pin, ExtInt

# Application version
APP_VERSION = "1.0.0"


def get_version():
    return APP_VERSION
    


BATTERY_OCV_TABLE = {
    "YT-LION-PINK-2600": {
        20: {
            4172: 100,
            4156: 95,
            4125: 90,
            4094: 85,
            4063: 80,
            4032: 75,
            4000: 70,
            3969: 65,
            3938: 60,
            3907: 55,
            3876: 50,
            3845: 45,
            3814: 40,
            3783: 35,
            3752: 30,
            3721: 25,
            3689: 20,
            3658: 15,
            3627: 10,
            3596: 5,
            3565: 0
        }
    }
}


class MyBattery:
    """
    Battery management class.

    Supports measurement via ADC, USB, or Battery Monitoring IC.

    Args:
        adc_args (tuple): (adc_num, adc_period, factor)
            adc_num: ADC channel num
            adc_period: Cyclic read ADC cycle period
            factor: calculation coefficient (optional)
        chrg_gpion (int): GPIO pin number for CHRG.
        stdby_gpion (int): GPIO pin number for STDBY.
        chrg_led_gpion (int): GPIO number connected to an LED
        battery_ocv (str): Battery OCV table key.
        use_batt_ic (bool): Flag to use Battery Monitoring IC.
    """

    def __init__(self, adc_args=None, chrg_gpion=None, stdby_gpion=None, pgood_gpion=None,
                 battery_ocv="YT-LION-PINK-2600", use_batt_ic=False):

        self.logger = None

        self.__energy = 100
        self.__temp = 20  # Default temperature in Celsius

        # ADC parameters
        self.__adc = None
        if adc_args:
            self.__adc_num, self.__adc_period, self.__factor = adc_args
            if not isinstance(self.__adc_num, int):
                raise TypeError("adc_args adc_num must be an integer.")
            if not isinstance(self.__adc_period, int):
                raise TypeError("adc_args adc_period must be an integer.")
            if not isinstance(self.__factor, float):
                raise TypeError("adc_args factor must be a float.")
            self.__adc = ADC()

        # Charging status parameters
        self.__charge_callback = None
        self.__charge_status = None
        self.__chrg_gpion = chrg_gpion
        self.__stdby_gpion = stdby_gpion
        self.__pgood_gpion = pgood_gpion
        self.__chrg_gpio = None
        self.__stdby_gpio = None
        self.__pgood_gpio = None
        self.__chrg_exint = None
        self.__stdby_exint = None
        self.__use_batt_ic = use_batt_ic

        # use chrg_gpion and stdy_gpion for charging status else use usb
        if self.__chrg_gpion is not None and (self.__stdby_gpion is not None or self.__pgood_gpion is not None):
            self.__init_charge()

        if self.__use_batt_ic:
            self.__init_batt_ic()

        if not BATTERY_OCV_TABLE.get(battery_ocv):
            raise ValueError("Battery OCV '{}' is not supported.", battery_ocv)
        self.__battery_ocv = battery_ocv

    def setLogger(self, level):
        """
        Set up logging configuration
        Args:
            log level (str): log level.
        """
        self.logger = log.getLogger(self.__class__.__name__)
        self.logger.setLevel(level)

    def __init_charge(self):
        """Initialize charging detection using CHRG and STDBY GPIOs."""
        self.__chrg_gpio = Pin(self.__chrg_gpion, Pin.IN, Pin.PULL_PU)
        self.__chrg_exint = ExtInt(self.__chrg_gpion, ExtInt.IRQ_RISING_FALLING,
                                   ExtInt.PULL_PU, self.__chrg_callback)
        self.__chrg_exint.enable()

        if self.__stdby_gpio is not None:
            self.__stdby_gpio = Pin(self.__stdby_gpion, Pin.IN, Pin.PULL_PU)
            self.__stdby_exint = ExtInt(self.__stdby_gpion, ExtInt.IRQ_RISING_FALLING,
                                        ExtInt.PULL_PU, self.__stdby_callback)
            self.__stdby_exint.enable()

        if self.__pgood_gpion is not None:
            self.__pgood_gpio = Pin(self.__pgood_gpion, Pin.IN, Pin.PULL_PU)
            self.__pgood_exint = ExtInt(self.__pgood_gpion, ExtInt.IRQ_RISING_FALLING,
                                        ExtInt.PULL_PU, self.__pgood_callback)
            self.__pgood_exint.enable()

        self.__update_charge_status()

    def __init_batt_ic(self):
        """Initialize battery monitoring using Battery Monitoring IC."""
        # Placeholder for Battery Monitoring IC initialization
        pass

    def __chrg_callback(self, args):
        """Callback for CHRG GPIO interrupt."""
        self.__update_charge_status()
        if callable(self.__charge_callback):
            self.__charge_callback(self.__charge_status)

    def __stdby_callback(self, args):
        """Callback for STDBY GPIO interrupt."""
        self.__update_charge_status()
        if callable(self.__charge_callback):
            self.__charge_callback(self.__charge_status)

    def __pgood_callback(self, args):
        """Callback for PGOOD GPIO interrupt."""
        self.__update_charge_status()
        if callable(self.__charge_callback):
            self.__charge_callback(self.__charge_status)

    def __update_charge_status(self):
        """Update charging status."""
        if self.__chrg_gpio and self.__stdby_gpio:
            chrg_level = self.__chrg_gpio.read()
            stdby_level = self.__stdby_gpio.read()
            if chrg_level == 1 and stdby_level == 1:
                self.__charge_status = 0  # Not charging
            elif chrg_level == 0 and stdby_level == 1:
                self.__charge_status = 1  # Charging
            elif chrg_level == 1 and stdby_level == 0:
                self.__charge_status = 2  # Charging complete
            else:
                raise ValueError("Invalid CHRG and STDBY GPIO states.")
        elif self.__chrg_gpio and self.__pgood_gpio:
            chrg_level = self.__chrg_gpio.read()
            pgood_level = self.__pgood_gpio.read()
            if pgood_level == 0 and chrg_level == 0:
                self.__charge_status = 1  # Charging
            elif pgood_level == 0 and chrg_level == 1:
                self.__charge_status = 2  # Charging complete
            elif pgood_level == 1 and chrg_level == 1:
                self.__charge_status = 0  # Not charging or no power
            else:
                raise ValueError("Invalid CHRG and PGOOD GPIO states.")
        else:
            self.__charge_status = None

    def __get_batt_ic_vbatt(self):
        """Get VBATT using Battery Monitoring IC."""
        # Placeholder for Battery Monitoring IC voltage retrieval
        pass

    def __get_power_vbatt(self):
        """Get VBATT using Power module."""
        return int(sum([Power.getVbatt() for _ in range(100)]) / 100)

    def __get_adc_vbatt(self):
        """Get VBATT using ADC."""
        self.__adc.open()
        utime.sleep_ms(10)
        adc_list = list()
        for i in range(self.__adc_period):
            adc_list.append(self.__adc.read(self.__adc_num))
            # utime.sleep_ms(self.__adc_period)
            utime.sleep_ms(1)

        adc_list.remove(min(adc_list))
        adc_list.remove(max(adc_list))
        adc_value = int(sum(adc_list) / len(adc_list))
        self.__adc.close()
        vbatt_value = adc_value * (self.__factor)
        return vbatt_value

    def __get_soc_from_dict(self, key, volt_arg):
        """Get battery energy from map"""
        if BATTERY_OCV_TABLE[self.__battery_ocv].get(key):
            volts = sorted(
                BATTERY_OCV_TABLE[self.__battery_ocv][key].keys(), reverse=True)
            pre_volt = 0
            # Determine whether the voltage is lower than the minimum voltage value of soc.
            volt_not_under = 0
            for volt in volts:
                if volt_arg > volt:
                    volt_not_under = 1
                    soc1 = BATTERY_OCV_TABLE[self.__battery_ocv][key].get(
                        volt, 0)
                    soc2 = BATTERY_OCV_TABLE[self.__battery_ocv][key].get(
                        pre_volt, 0)
                    break
                else:
                    pre_volt = volt
            if pre_volt == 0:  # Input Voltarg > Highest Voltarg
                return soc1
            elif volt_not_under == 0:
                return 0
            else:
                return soc2 - (soc2 - soc1) * (pre_volt - volt_arg) // (pre_volt - volt)
            
        else:
            print("Key not found")

    def __get_soc(self, temp, volt_arg):
        """Get battery energy by temperature and voltage"""
        if temp > 30:
            return self.__get_soc_from_dict(55, volt_arg)
        elif temp < 10:
            return self.__get_soc_from_dict(0, volt_arg)
        else:
            return self.__get_soc_from_dict(20, volt_arg)

    def set_temp(self, temp):
        """Set current temperature."""
        if isinstance(temp, (int, float)):
            self.__temp = temp
            return True
        return False

    def set_charge_callback(self, charge_callback):
        """Set callback for charging status changes."""
        if self.__chrg_gpion is not None and (self.__stdby_gpion is not None or self.__pgood_gpion is not None):
            if callable(charge_callback):
                self.__charge_callback = charge_callback
                return True
        return False

    @property
    def voltage(self):
        """Get battery voltage."""
        if self.__use_batt_ic:
            return self.__get_batt_ic_vbatt()
        elif self.__adc:
            return self.__get_adc_vbatt()
        else:
            return self.__get_power_vbatt()

    @property
    def energy(self):
        """Get battery energy percentage."""
        self.__energy = self.__get_soc(self.__temp, self.voltage)
        return self.__energy

    @property
    def charge_status(self):
        """Get charging status.

        Returns:
            int: 
            0 - Not charging 
            1 - Charging 
            2 - Charging complete
            None - Unknown
        """
        self.__update_charge_status()
        return self.__charge_status
