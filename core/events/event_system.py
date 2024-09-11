from collections import defaultdict

class EventSystem:
    def __init__(self):
        self.listeners = defaultdict(list)

    def register_listener(self, event_type, listener):
        self.listeners[event_type].append(listener)

    def trigger_event(self, event_type, data=None):
        for listener in self.listeners.get(event_type, []):
            listener(data)
