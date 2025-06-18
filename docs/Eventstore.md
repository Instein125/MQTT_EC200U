# Eventstore.py

## Overview

`Eventstore.py` implements a lightweight, in-memory **event bus** (publish/subscribe system) for decoupled communication between different components of the project. It allows screens, services, and hardware abstraction layers to communicate by publishing and subscribing to named events, without direct references to each other.

This pattern is essential for building modular, maintainable, and scalable applications, especially in event-driven architectures like this IoT demo.

## Features

- **Publish/Subscribe Mechanism**: Components can subscribe to specific event names and receive notifications when those events are published
- **Loose Coupling**: Components do not need to know about each other; they only interact via events
- **Multiple Subscribers**: Any number of callbacks can be registered for a single event
- **Thread-Safe (if implemented)**: Can be extended for thread safety if used in multi-threaded environments

## Typical Usage

### 1. Subscribing to Events

A component (e.g., a screen or service) registers a callback to be notified when a specific event occurs:

```python
import usr.Eventstore as Eventstore

def on_network_status(event, msg):
    print("Network status changed:", event_data)

EventStore.subscribe("network.status", on_network_status)
```

### 2. Publishing Events

Any component can publish an event, optionally passing data:

```python
EventStore.publish("network.status", {"connected": True, "ip": "192.168.1.10"})
```

All subscribers to `"network.status"` will receive the event and the data.

## API Reference

### `EventStore.subscribe(event_name, callback, owner)`

**Parameters:**
- **event_name** (`str`): The name of the event to subscribe to
- **callback** (`callable`): The function to call when the event is published. Should accept one argument (the event data)
- **owner**: Optional owner object for tracking (recommended)

Registers the callback for the specified event.

### `EventStore.unsubscribe(event_name, subscription_id)`

**Parameters:**
- **event_name** (`str`): The event name
- **subscription_id** (`callable`): The subscription ID returned by subscribe()

Unsubscribe from an event using the subscription ID.

### `EventStore.unsubscribe_by_owner(owner)`

**Parameters:**
- **owner**: The owner object

Remove all subscriptions belonging to a specific owner.

### `EventStore.publish(event_name, data=None)`

**Parameters:**
- **event_name** (`str`): The event to publish
- **data** (optional): Data to pass to subscribers

Calls all registered callbacks for the event, passing `data` as the argument. Publish event synchronously (Blocking).

### `EventStore.publish_async(event_name, data=None)`

**Parameters:**
- **event_name** (`str`): The event to publish
- **data** (optional): Data to pass to subscribers

Publish event asynchronously to all subscribers.(Non Blocking)

### `EventStore.set_log(log_adapter)`

**Parameters:**
- **log_adapter** (`log`): log object for logging

Set the log adapter for logging.

### `EventStore.get_subscriber_count(event_name)`

**Parameters:**
- **event_name** (`str`): event to get the number of subscribers

Get the number of active subscribers for an event.

### `EventStore.cleanup()`

Manually cleanup the dead subscriptions. Call this periodically to clean the dead subscriptions

## Example

```python
import usr.Eventstore as EventStore

def on_mqtt_message(msg):
    print("Received MQTT message:", msg)

# Subscribe to MQTT messages
EventStore.subscribe("mqtt.message", on_mqtt_message)

# Later, when an MQTT message is received:
EventStore.publish("mqtt.message", {"topic": "test", "payload": "hello"})
```

## Best Practices

- Use **unique, descriptive event names** (e.g., `"network.status"`, `"mqtt.message"`)
- **Unsubscribe** when a component is destroyed to avoid memory leaks
- Keep event handlers **fast and non-blocking** to avoid delaying other subscribers

## Role in the Project

- **Screens** subscribe to events to update the UI (e.g., show new messages, update status)
- **Services** publish events when hardware/network/MQTT state changes
- **Hardware abstraction** can publish events (e.g., battery low) for the UI or services to react

## Summary

`Eventstore.py` is the backbone of the project's event-driven architecture, enabling modular, decoupled, and maintainable code by providing a simple, flexible event bus for all components to communicate efficiently.