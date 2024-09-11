class PluginProvider:
    def __init__(self, app):
        self.app = app
        self.collectors = []
        self.processors = []

    def register(self):
        raise NotImplementedError("Each plugin must implement its own register method.")

    def get_collectors(self):
        return self.collectors

    def get_processors(self):
        return self.processors
