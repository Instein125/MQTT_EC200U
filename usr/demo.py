'''
File: main.py
Created Date: Tuesday June 10th 2025
Author: Prashant Bhandari
Last Modified: We/06/2025 09:37:37
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''
from usr.ui import Ui
from usr.screens.WelcomeScreen import WelcomeScreen
from usr.screens.ConnectingScreen import ConnectingScreen
from usr.screens.MessageScreen import MessageScreen
import usr.services.time_service as time_service
import usr.services.network_service as network_service
import utime
import usr.Eventstore as Eventstore
import usr.services.mqtt_service as mqtt_service


def main():
    ui = Ui()
    ui.add_screen(WelcomeScreen())
    ui.add_screen(ConnectingScreen())
    ui.add_screen(MessageScreen())

    time_service.run_time_updater()

    ui.start()
    ret = network_service.init()
    utime.sleep(2)

    if ret == 0:
        #  Delete screen as it is not needed to remove subscriptions
        Eventstore.publish("destroy_screen", "ConnectingScreen")
        mqtt_service.mqtt_connect()


if __name__ == '__main__':
    main()
