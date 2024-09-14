class EventSystem:
    def __init__(self):
        self.listeners = {}

    def register_listener(self, event_name, callback):
        self.listeners.setdefault(event_name, []).append(callback)

    def trigger_event(self, event_name, *args, **kwargs):
        for callback in self.listeners.get(event_name, []):
            callback(*args, **kwargs)
