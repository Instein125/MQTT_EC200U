# EC200U MQTT Demo Project

## Overview

This project demonstrates a modular, event-driven architecture for an IoT device based on the Quectel EC200U module. It features a graphical user interface (GUI) using LVGL, MQTT communication, network management, and event-driven screen transitions. The codebase is organized for maintainability, scalability, and clear separation of concerns.

## Project Structure

```
usr/
├── assets/                 # Image assets for UI
├── comb_firmware/          # Firmware files
├── extensions/             # Hardware abstraction and drivers
│   ├── my_battery.py       # Battery management
│   ├── my_button.py        # Button abstraction
│   ├── my_mqtts.py         # MQTT client wrapper
│   ├── my_netmanager.py    # Network management
│   └── Lcd_lvgl_init.py    # LCD/LVGL initialization
├── screens/                # UI screens (LVGL-based)
│   ├── ConnectingScreen.py
│   ├── MessageScreen.py
│   ├── WelcomeScreen.py
│   └── screen.py           # Base screen class
├── services/               # Application logic/services
│   ├── button_service.py
│   ├── mqtt_service.py
│   ├── network_service.py
│   └── time_service.py
├── config.py               # Main configuration file
├── demo.py                 # Main entry point
├── Eventstore.py           # Event bus for decoupled communication
├── mqtt_ca.crt             # MQTT SSL certificate
└── ui.py                   # UI manager
```

## Core Components & Interactions

### 1. Configuration (`config.py`)

Centralizes all hardware, MQTT, display, and asset settings. Used by all modules to ensure consistent configuration.

### 2. Eventstore (`Eventstore.py`)

- Implements a publish/subscribe event bus
- Enables decoupled communication between screens, services, and hardware drivers
- Example: Screens subscribe to "mqtt.status" or "network.status" events to update UI reactively

### 3. Extensions (Hardware Abstraction Layer)

- **`my_battery.py`**: Reads battery status via ADC or battery IC, exposes battery percentage and charging state
- **`my_netmanager.py`**: Handles SIM, modem, and network registration. Provides connect/disconnect/reconnect logic and status callbacks
- **`my_mqtts.py`**: Wraps the MQTT client, manages connection, reconnection, and message callbacks
- **`my_button.py`**: Abstracts button input

These modules are used by services to interact with hardware in a platform-agnostic way.

### 4. Services

- **`network_service.py`**: Manages network state using `MyNetManager`. Publishes network status events
- **`mqtt_service.py`**: Manages MQTT connection using `MyMqttClient`. Handles message receive, error callbacks, and publishes MQTT status/events
- **`time_service.py`**: Provides time updates for UI
- **`button_service.py`**: Handles button events and publishes them to the event bus

### 5. UI Layer

- **`ui.py`**: Initializes LVGL, manages screen stack, and handles screen transitions
- **Screens (`screens/`)**: Each screen (Welcome, Connecting, Message) is a class that:
  - Creates LVGL widgets for its UI
  - Subscribes to relevant events (e.g., time, network, MQTT status)
  - Updates its widgets in response to events
  - Publishes events (e.g., button presses, screen transitions)

### 6. Main Application (`demo.py`)

- Instantiates the UI and all screens
- Starts the time updater
- Initializes the network and, upon success, transitions from the ConnectingScreen to the MessageScreen and starts MQTT

## Component Interaction Flow

### 1. Startup
- `demo.py` creates the UI and all screens
- The WelcomeScreen is shown first, then transitions to ConnectingScreen

### 2. Network Initialization
- `network_service.init()` uses `MyNetManager` to connect to the network
- On success, publishes a "network.status" event
- The ConnectingScreen listens for this event and transitions to MessageScreen

### 3. MQTT Connection
- After network is ready, `mqtt_service.mqtt_connect()` is called
- `MyMqttClient` connects to the broker, subscribes to topics, and sets up message callbacks
- MQTT status and messages are published as events

### 4. UI Updates
- Screens subscribe to events (e.g., "mqtt.status", "mqtt.message", "time.update", "button.event")
- When an event is published, the relevant screen updates its widgets accordingly (e.g., show new message, update battery, show connection status)

### 5. Button Handling
- Button presses are handled by `button_service.py` and published as "button.event" events
- Screens can subscribe to these to implement navigation or actions

## Codebase Maintenance

- **Modularity**: Each hardware or service abstraction is in its own file/class
- **Configuration-Driven**: All hardware and service parameters are set in `config.py`
- **Event-Driven**: All cross-component communication is via the event bus, minimizing direct dependencies
- **Screen Isolation**: Each screen manages its own UI and event subscriptions, making it easy to add or modify screens
- **Logging**: Each major class supports logger injection for debugging and diagnostics

## Extending the Project

- **Add a new screen**: Create a new class in `screens/`, add it to the UI in `demo.py`, and subscribe to relevant events
- **Add new hardware support**: Implement a new extension in `extensions/` and expose its API via a service in `services/`
- **Change MQTT or network settings**: Update `config.py` only; all modules will use the new settings automatically


## Technologies Used

- **Hardware**: Quectel EC200U module
- **UI Framework**: LVGL (Light and Versatile Graphics Library)
- **Communication**: MQTT over SSL/TLS
- **Programming Language**: Python (MicroPython)
- **Architecture Pattern**: Event-driven, Publisher-Subscriber