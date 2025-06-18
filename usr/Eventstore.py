'''
File: eventstore.py
Created Date: Thursday June 12th 2025
Author: Samman Shrestha
Last Modified: Tu/06/2025 05:21:18
Modified By: Samman Shrestha
Copyright (c) 2025 YARSA TECH
'''

import _thread
import gc
import time
import log

# Set up logging configuration
log.basicConfig(level=log.INFO)
event_log = log.getLogger("EVENT")

class EventStore(object):
    def __init__(self):
        self._subscribers = {}  # Dict[str, List[tuple]]
        self._lock_flag = False  # Simple lock using flag
        self._subscription_counter = 0
        self.log = None

    def _acquire_lock(self):
        timeout = 100  # 100ms timeout
        start_time = time.ticks_ms()
        
        while self._lock_flag:
            if time.ticks_diff(time.ticks_ms(), start_time) > timeout:
                raise Exception("Lock timeout")
            time.sleep_ms(1)
        
        self._lock_flag = True

    def _release_lock(self):
        """Release the simple lock"""
        self._lock_flag = False
    
    def subscribe(self, event, callback, owner=None):
        """
        Subscribe to an event with a callback function.
        
        Args:
            event: The event name to subscribe to
            callback: The callback function to execute
            owner: Optional owner object for tracking (recommended)
            
        Returns:
            subscription_id: Unique identifier for this subscription
        """
        self._acquire_lock()
        try:
            # Initialize event list if needed
            if event not in self._subscribers:
                self._subscribers[event] = []
            
            # Generate unique subscription ID
            self._subscription_counter += 1
            subscription_id = "sub_{}_{}_{}".format(
                event.replace(".", "_"), 
                id(callback) if callback else 0,
                self._subscription_counter
            )
            
            # Store subscription info
            subscription_info = {
                'id': subscription_id,
                'callback': callback,
                'owner': owner,
                'active': True
            }
            
            self._subscribers[event].append(subscription_info)
            
            return subscription_id
            
        finally:
            self._release_lock()
    
    def unsubscribe(self, event, subscription_id):
        """
        Unsubscribe from an event using the subscription ID.
        
        Args:
            event: The event name
            subscription_id: The subscription ID returned by subscribe()
            
        Returns:
            bool: True if successfully unsubscribed, False otherwise
        """
        self._acquire_lock()
        try:
            if event not in self._subscribers:
                return False
            
            # Find and remove the subscription
            for i, sub_info in enumerate(self._subscribers[event]):
                if sub_info['id'] == subscription_id:
                    del self._subscribers[event][i]
                    return True
            
            return False
            
        finally:
            self._release_lock()
    
    def unsubscribe_by_owner(self, owner):
        """
        Remove all subscriptions belonging to a specific owner.
        
        Args:
            owner: The owner object
            
        Returns:
            int: Number of subscriptions removed
        """
        self._acquire_lock()
        try:
            removed_count = 0
            
            for event in list(self._subscribers.keys()):
                original_length = len(self._subscribers[event])
                self._subscribers[event] = [
                    sub for sub in self._subscribers[event] 
                    if sub['owner'] is not owner
                ]
                removed_count += original_length - len(self._subscribers[event])
                
                # Clean up empty event lists
                if not self._subscribers[event]:
                    del self._subscribers[event]
            
            return removed_count
            
        finally:
            self._release_lock()

    def unsubscribe_all(self, event):
        """
        Remove all subscribers for a specific event.
        
        Args:
            event: The event name
            
        Returns:
            int: Number of subscribers removed
        """
        self._acquire_lock()
        try:
            if event in self._subscribers:
                count = len(self._subscribers[event])
                del self._subscribers[event]
                return count
            return 0
            
        finally:
            self._release_lock()

    def _cleanup_dead_owners(self):
        """
        Clean up subscriptions where owner objects might be dead.
        """
        self._acquire_lock()
        try:
            for event in list(self._subscribers.keys()):
                active_subs = []
                
                for sub_info in self._subscribers[event]:
                    # Keep subscriptions that are explicitly active or have no owner
                    if sub_info['active'] and (sub_info['owner'] is None or self._is_owner_alive(sub_info['owner'])):
                        active_subs.append(sub_info)
                
                if active_subs:
                    self._subscribers[event] = active_subs
                else:
                    del self._subscribers[event]
                    
        finally:
            self._release_lock()


    def _is_owner_alive(self, owner):
        """
        Check if owner object is still alive.
        In QuecPython, we rely on the owner's active state or existence.
        """
        if owner is None:
            return True
        
        # Check if owner has an 'active' attribute
        if hasattr(owner, 'active'):
            return getattr(owner, 'active', True)
        
        # If owner exists and is accessible, assume it's alive
        try:
            # Try to access some attribute to see if object is valid
            str(owner)
            return True
        except:
            return False
    
    def _get_active_callbacks(self, event):
        """Get all active callbacks for an event."""
        if event not in self._subscribers:
            return []
        
        active_callbacks = []
        dead_subscriptions = []
        
        for sub_info in self._subscribers[event]:
            if sub_info['active'] and sub_info['callback']:
                # Check if owner is still alive (if specified)
                if sub_info['owner'] is None or self._is_owner_alive(sub_info['owner']):
                    active_callbacks.append(sub_info['callback'])
                else:
                    dead_subscriptions.append(sub_info['id'])
        
        # Remove dead subscriptions
        if dead_subscriptions:
            self._subscribers[event] = [
                sub for sub in self._subscribers[event] 
                if sub['id'] not in dead_subscriptions
            ]
        
        return active_callbacks
    
    def publish_async(self, event, *args):
        """
        Publish an event asynchronously to all subscribers.
        
        Args:
            event: The event name
            *args: Arguments to pass to callbacks
            
        Returns:
            int: Number of callbacks executed
        """
        self._acquire_lock()
        try:
            callbacks = self._get_active_callbacks(event)
        finally:
            self._release_lock()
        
        if not callbacks:
            return 0
        
        executed_count = 0
        for callback in callbacks:
            try:
                _thread.start_new_thread(self._safe_callback_execution, 
                                       (callback, event, args, True))
                executed_count += 1
            except Exception as e:
                if self.log:
                    self.log.error("Failed to start async thread for event '{}': {}".format(event, e))
                else:
                    print("Failed to start async thread for event '{}': {}".format(event, e))
        
        if self.log:
            self.log.info("ASYNC executed event '{}' with {} callbacks".format(event, executed_count))
        
        return executed_count
    
    def publish_sync(self, event, *args):
        """
        Publish an event synchronously to all subscribers.
        
        Args:
            event: The event name
            *args: Arguments to pass to callbacks
            
        Returns:
            list: List of results from all callbacks
        """
        self._acquire_lock()
        try:
            callbacks = self._get_active_callbacks(event)
        finally:
            self._release_lock()
        
        results = []
        for callback in callbacks:
            result = self._safe_callback_execution(callback, event, args, False)
            results.append(result)
        
        if self.log:
            self.log.info("SYNC executed event '{}' with {} callbacks".format(event, len(callbacks)))
        
        return results
    
    def _safe_callback_execution(self, callback, event, args, is_async):
        """Safely execute a callback with error handling and logging."""
        try:
            # Support both old signature (event, msg) and new signature
            if len(args) == 1:
                # Old signature: callback(event, msg)
                result = callback(event, args[0])
            elif len(args) == 0:
                # Just event
                result = callback(event)
            else:
                # Multiple arguments: callback(event, arg1, arg2, ...)
                result = callback(event, *args)
            
            return result
            
        except Exception as e:
            error_msg = "Error executing callback for event '{}': {}".format(event, e)
            if self.log:
                self.log.error(error_msg)
            else:
                print(error_msg)
            return None
    
    def get_subscriber_count(self, event):
        """Get the number of active subscribers for an event."""
        self._acquire_lock()
        try:
            return len(self._get_active_callbacks(event))
        finally:
            self._release_lock()
    
    def get_all_events(self):
        """Get a list of all events that have subscribers."""
        self._acquire_lock()
        try:
            return [event for event, subs in self._subscribers.items() if subs]
        finally:
            self._release_lock()
    
    def set_log(self, log_adapter):
        """Set the log adapter for logging."""
        self.log = log_adapter
    
    def cleanup(self):
        """Manual cleanup of dead subscriptions - call periodically"""
        self._cleanup_dead_owners()
        # Force garbage collection
        gc.collect()
    
    def debug_info(self):
        """Print debug information about current subscriptions"""
        self._acquire_lock()
        try:
            print("=== EventStore Debug Info ===")
            for event, subs in self._subscribers.items():
                print("Event '{}': {} subscribers".format(event, len(subs)))
                for sub in subs:
                    owner_info = "owner={}".format(type(sub['owner']).__name__ if sub['owner'] else "None")
                    print("  - {} ({})".format(sub['id'], owner_info))
        finally:
            self._release_lock()


# Global instance and convenience functions
my_eventstore = EventStore()
# my_eventstore.set_log(event_log)

def subscribe(event, callback, owner=None):
    """
    Subscribe to an event with a callback function.
    
    Args:
        event: The event name to subscribe to
        callback: The callback function to execute
        owner: Optional owner object for tracking (recommended)
        
    Returns:
        subscription_id: Unique identifier for this subscription
    """
    return my_eventstore.subscribe(event, callback, owner)

def unsubscribe(event, subscription_id):
    """Unsubscribe from an event using the subscription ID."""
    return my_eventstore.unsubscribe(event, subscription_id)

def unsubscribe_by_owner(owner):
    """Remove all subscriptions belonging to a specific owner."""
    return my_eventstore.unsubscribe_by_owner(owner)

def publish(event, *args):
    """Publish event synchronously (default behavior)."""
    return publish_sync(event, *args)

def publish_async(event, *args):
    """Publish event asynchronously to all subscribers."""
    return my_eventstore.publish_async(event, *args)

def publish_sync(event, *args):
    """Publish event synchronously to all subscribers."""
    return my_eventstore.publish_sync(event, *args)

def set_log(log_adapter):
    """Set the log adapter for logging."""
    my_eventstore.set_log(log_adapter)

def get_subscriber_count(event):
    """Get the number of active subscribers for an event."""
    return my_eventstore.get_subscriber_count(event)

def cleanup():
    """Manual cleanup of dead subscriptions - call periodically"""
    my_eventstore.cleanup()

def debug_info():
    """Print debug information about current subscriptions"""
    my_eventstore.debug_info()

# Backward compatibility
def append(event, callback):
    """Deprecated: Use subscribe() instead."""
    return subscribe(event, callback)