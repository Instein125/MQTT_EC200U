'''
File: MessageScreen.py
Created Date: Monday June 9th 2025
Author: Prashant Bhandari
Last Modified: We/06/2025 11:47:02
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''
import utime
import _thread
import usr.Eventstore as Eventstore
from usr.screens.screen import Screen
import usr.services.time_service as time_service
import usr.services.mqtt_service  as mqtt_service
from usr.services.button_service import ButtonService
from usr.config import Config

asset_cfg = Config.ASSETS
scroll_cfg = Config.SCROLL

class MessageScreen(Screen):
    def __init__(self):
        self.screen = None
        self.name = 'MessageScreen'

        # UI element references
        self.message_container = None
        self.message_text = None
        self.server_id_text = None
        self.client_id_text = None
        self.topic_text = None
        self.last_message_timestamp = 0

        # Button flags - make them instance variables
        self.flag_scrollup = False
        self.flag_scrolldown = False
        self.flag_scrollup_long_press = False
        self.flag_scrolldown_long_press = False

        # Button instances
        self.button_scrollup = None
        self.button_scrolldown = None

        # Initialize buttons
        self.button_service = ButtonService(
            cb_up=self.__cb_button_scrollup_press,
            cb_down=self.__cb_button_scrolldown_press,
            cb_up_release=self.__cb_button_scrollup_release,
            cb_down_release=self.__cb_button_scrolldown_release
        )

        self.button_subscription_id = None
        self.scroll_up_active = False
        self.scroll_down_active = False
        self.scroll_thread_running = False

    def create(self):
        # Create the screen object and store it as instance variable
        self.screen = self.lv.obj()
        self.screen.set_size(self.height, self.width)
        self.screen.set_scrollbar_mode(self.lv.SCROLLBAR_MODE.OFF)

        # Set style for MessageScreen, Part: lv.PART.MAIN, State: lv.STATE.DEFAULT.
        self.screen.set_style_bg_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_color(self.lv.color_hex(
            0x000000), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.screen.set_style_bg_grad_dir(
            self.lv.GRAD_DIR.NONE, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create self.MessageScreen_Time
        self.MessageScreen_Time = self.lv.label(self.screen)
        self.MessageScreen_Time.set_text(time_service.get_time() + "\n")
        self.MessageScreen_Time.set_long_mode(self.lv.label.LONG.WRAP)
        self.MessageScreen_Time.set_width(self.lv.pct(100))
        self.MessageScreen_Time.set_pos(110, 4)
        self.MessageScreen_Time.set_size(100, 16)

        # Set style for self.MessageScreen_Time
        self.MessageScreen_Time.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_color(self.lv.color_hex(
            0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_text_align(
            self.lv.TEXT_ALIGN.CENTER, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.MessageScreen_Time.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_BatteryPercent
        MessageScreen_BatteryPercent = self.lv.label(self.screen)
        MessageScreen_BatteryPercent.set_text("80%")
        MessageScreen_BatteryPercent.set_long_mode(self.lv.label.LONG.WRAP)
        MessageScreen_BatteryPercent.set_width(self.lv.pct(100))
        MessageScreen_BatteryPercent.set_pos(216, 4)
        MessageScreen_BatteryPercent.set_size(100, 16)

        # Set style for MessageScreen_BatteryPercent
        MessageScreen_BatteryPercent.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_color(
            self.lv.color_hex(0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_text_align(
            self.lv.TEXT_ALIGN.RIGHT, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_BatteryPercent.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_MessageContainer
        self.message_container = self.lv.obj(self.screen)
        self.message_container.set_pos(0, 129)
        self.message_container.set_size(320, 111)
        self.message_container.set_scrollbar_mode(self.lv.SCROLLBAR_MODE.ON)
        self.message_container.set_scroll_dir(self.lv.DIR.VER)

        # Set style for MessageScreen_MessageContainer
        self.message_container.set_style_border_width(
            2, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_border_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_border_color(self.lv.color_hex(
            0x2195f6), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_border_side(
            self.lv.BORDER_SIDE.FULL, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_bg_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_bg_color(self.lv.color_hex(
            0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_bg_grad_dir(
            self.lv.GRAD_DIR.NONE, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_container.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_MessageText
        self.message_text = self.lv.label(self.message_container)
        self.message_text.set_text("")
        self.message_text.set_long_mode(self.lv.label.LONG.WRAP)
        self.message_text.set_width(300)
        self.message_text.set_pos(5, 5)
        # self.message_text.set_size(280, 111)

        # Set style for MessageScreen_MessageText
        self.message_text.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_color(self.lv.color_hex(
            0x000000), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_text_align(
            self.lv.TEXT_ALIGN.LEFT, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.message_text.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_Img4G
        MessageScreen_Img4G = self.lv.img(self.screen)
        MessageScreen_Img4G.set_src(asset_cfg["img_4g"])
        MessageScreen_Img4G.add_flag(self.lv.obj.FLAG.CLICKABLE)
        MessageScreen_Img4G.set_pivot(50, 50)
        MessageScreen_Img4G.set_angle(0)
        MessageScreen_Img4G.set_pos(27, 4)
        MessageScreen_Img4G.set_size(20, 14)
        MessageScreen_Img4G.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_Img4G.set_style_clip_corner(
            True, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_Img4G.set_style_img_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_ImgSignal
        MessageScreen_ImgSignal = self.lv.img(self.screen)
        MessageScreen_ImgSignal.set_src(asset_cfg["img_signal"])
        MessageScreen_ImgSignal.add_flag(self.lv.obj.FLAG.CLICKABLE)
        MessageScreen_ImgSignal.set_pivot(50, 50)
        MessageScreen_ImgSignal.set_angle(0)
        MessageScreen_ImgSignal.set_pos(4, 4)
        MessageScreen_ImgSignal.set_size(20, 14)
        MessageScreen_ImgSignal.set_style_img_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_ImgSignal.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        MessageScreen_ImgSignal.set_style_clip_corner(
            True, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_ServerIdText
        self.server_id_text = self.lv.label(self.screen)
        self.server_id_text.set_text("Server Id: "+ mqtt_service.MQTT_SERVER)
        self.server_id_text.set_long_mode(self.lv.label.LONG.WRAP)
        self.server_id_text.set_width(self.lv.pct(100))
        self.server_id_text.set_pos(5, 43)
        self.server_id_text.set_size(350, 16)
        self.server_id_text.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_color(self.lv.color_hex(
            0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_text_align(
            self.lv.TEXT_ALIGN.LEFT, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.server_id_text.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_TopicText
        self.topic_text = self.lv.label(self.screen)
        self.topic_text.set_text("Status: "+mqtt_service.mqtt_get_status())
        self.topic_text.set_long_mode(self.lv.label.LONG.WRAP)
        self.topic_text.set_width(self.lv.pct(100))
        self.topic_text.set_pos(5, 95)
        self.topic_text.set_size(280, 16)
        self.topic_text.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_color(self.lv.color_hex(
            0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_text_align(
            self.lv.TEXT_ALIGN.LEFT, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.topic_text.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)

        # Create MessageScreen_ClientIdText
        self.client_id_text = self.lv.label(self.screen)
        self.client_id_text.set_text("Client Id: " + mqtt_service.CLIENT_ID)
        self.client_id_text.set_long_mode(self.lv.label.LONG.WRAP)
        self.client_id_text.set_width(self.lv.pct(100))
        self.client_id_text.set_pos(5, 70)
        self.client_id_text.set_size(280, 16)
        self.client_id_text.set_style_border_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_radius(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_color(self.lv.color_hex(
            0xffffff), self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_font(
            self.lv.font_montserrat_14, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_opa(
            255, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_letter_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_line_space(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_text_align(
            self.lv.TEXT_ALIGN.LEFT, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_bg_opa(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_pad_top(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_pad_right(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_pad_bottom(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_pad_left(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.client_id_text.set_style_shadow_width(
            0, self.lv.PART.MAIN | self.lv.STATE.DEFAULT)
        self.screen.update_layout()

        Eventstore.subscribe("time.update", self.__update_time_cb, owner=self)
        Eventstore.subscribe("mqtt.status", self.__mqtt_status_cb, owner=self)
        Eventstore.subscribe("mqtt.message", self.__refresh_message_display_from_mqtt, owner=self)
        self.button_subscription_id = Eventstore.subscribe("button.event", self.__button_event_cb, owner=self)

    def destroy(self):
        self.active = False
        Eventstore.unsubscribe_by_owner(self)  # Clean up all subscriptions

    def __start_scroll_thread(self):
        if self.scroll_thread_running:
            return  # Prevent starting multiple threads
        
        self.scroll_thread_running = True

        def scroll_loop():
            base_scroll = scroll_cfg["base_scroll"]           
            max_scroll = scroll_cfg["max_scroll"]            
            scroll_increment = scroll_cfg["scroll_increment"]      
            step_interval = scroll_cfg["step_interval"]        
            scroll_interval = scroll_cfg["scroll_interval"]      

            held_time = 0              # Total time button is being held
            try:
                while self.scroll_up_active or self.scroll_down_active:
                    # Calculate scroll step based on held time
                    step = min(base_scroll + (held_time // step_interval) * scroll_increment, max_scroll)
                    if self.scroll_up_active:
                        self.__limited_scroll(-step)
                    elif self.scroll_down_active:
                        self.__limited_scroll(step)
                    utime.sleep_ms(scroll_interval)
                    held_time+=scroll_interval
            finally:
                self.scroll_thread_running = False  # Thread has exited

        _thread.start_new_thread(scroll_loop, ())
    
    def __button_event_cb(self, event, msg):
        if msg == "SCROLL_UP":
            self.scroll_up_active = True
            self.scroll_down_active = False
            self.__start_scroll_thread()

        elif msg == "SCROLL_DOWN":
            self.scroll_down_active = True
            self.scroll_up_active = False
            self.__start_scroll_thread()

        elif msg == "SCROLL_UP_STOP":
            self.scroll_up_active = False

        elif msg == "SCROLL_DOWN_STOP":
            self.scroll_down_active = False

    def __update_time_cb(self, event, time_str):
        """
        Update the time shown on the ConnectingScreen_Time label.

        Args:
            time_str (str): The current time as a string (e.g., "11:45:01")
        """
        self.MessageScreen_Time.set_text(time_str + "\n")

    def __mqtt_status_cb(self, event, msg):
        self.topic_text.set_text("Status: "+mqtt_service.mqtt_get_status())
        if msg == "CONNECTED":
            pass
        elif msg == "CONNECTING":
            pass
        elif msg == "DISCONNECTED":
            pass
        elif msg == "RECONNECTING":
            pass
        elif msg == "FAILED":
            pass

    def __cb_button_scrollup_press(self):
        """Callback for scrollup button press"""
        Eventstore.publish("button.event", "SCROLL_UP")

    def __cb_button_scrolldown_press(self):
        """Callback for scrolldown button press"""
        Eventstore.publish("button.event", "SCROLL_DOWN")

    def __cb_button_scrollup_release(self):
        """Callback for scrollup button release"""
        Eventstore.publish("button.event", "SCROLL_UP_STOP")

    def __cb_button_scrolldown_release(self):
        """Callback for scrolldown button release"""
        Eventstore.publish("button.event", "SCROLL_DOWN_STOP")

    def __scroll_to_bottom(self):
        """Scroll the message container to the bottom"""
        if self.message_container:
            max_scroll = self.__get_scroll_limits() + 50
            self.message_container.scroll_to_y(max_scroll, True)

    def __get_scroll_limits(self):
        """Get max scrollable distance for message container."""
        if self.message_text and self.message_container:
            content_height = self.message_text.get_height()
            container_height = self.message_container.get_height()
            return max(0, content_height - container_height)
        return 0
    
    def __limited_scroll(self, dy):
        """Scroll the message container by dy, limited to content size."""
        if not self.message_container:
            return

        current_y = self.message_container.get_scroll_y()
        max_scroll = self.__get_scroll_limits()
        new_y = current_y + dy

        # Clamp to limits
        new_y = max(0, min(new_y, max_scroll+50))

        if new_y != current_y:
            self.message_container.scroll_to_y(new_y, True)

    def __refresh_message_display_from_mqtt(self, event, msg):
        """
        Refresh the message_text UI with the latest MQTT message.
        """
        try:
            # Validate message structure
            if not isinstance(msg, dict) or 'message' not in msg:
                # print("Invalid MQTT message format:", msg)
                return
            
            # Extract and format data
            raw_msg = msg['message']
            topic = msg.get('topic', 'Unknown')
            timestamp = msg.get('timestamp', 0)

            cleaned_msg = raw_msg.strip().replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
            formatted_msg = "Msg: {}\nTime: {}".format(cleaned_msg, int(timestamp))

            # Append to existing display text
            existing_text = self.message_text.get_text()
            updated_text = formatted_msg if not existing_text else existing_text + "\n" + formatted_msg

            self.message_text.set_text(updated_text)
            self.__scroll_to_bottom()
        except Exception as e:
            error_msg = "Error getting MQTT data: {}".format(str(e))
            self.message_text.set_text(error_msg)
            print("Error in refresh_message_display_from_mqtt:", e)