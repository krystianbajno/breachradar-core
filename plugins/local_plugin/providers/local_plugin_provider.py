from core.providers.plugin_provider import PluginProvider
from plugins.local_plugin.services.local_service import LocalService
from plugins.local_plugin.collectors.local_collector import LocalCollector
from plugins.local_plugin.processors.local_processor import LocalProcessor

class LocalPluginProvider(PluginProvider):
    def __init__(self, app):
        super().__init__(app)

    def register(self):
        """Register LocalPlugin-specific services, collectors, and processors."""

        self.app.bind('LocalService', lambda: LocalService(system_tick=self.app.configuration.get("system_tick")))


        local_collector = LocalCollector(self.app)
        local_processor = LocalProcessor(self.app)

        self.collectors.append(local_collector)
        self.processors.append(local_processor)
