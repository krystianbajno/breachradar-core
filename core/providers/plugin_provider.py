class PluginProvider:
    def __init__(self, app):
        self.app = app
        self.collectors = []
        self.processors = []

    def register(self):
        """Register services, collectors, and processors. To be overridden by the plugin-specific provider."""
        raise NotImplementedError("Each plugin must implement its own register method.")

    def get_collectors(self):
        """Return the list of collectors."""
        return self.collectors

    def get_processors(self):
        """Return the list of processors."""
        return self.processors
