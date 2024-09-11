from concurrent.futures import ThreadPoolExecutor
from core.events.event_system import EventSystem
from core.plugins.plugin_loader import PluginLoader
from core.systems.collector_system import CollectorSystem
from core.systems.processing_system import ProcessingSystem

class ECSManager:
    def __init__(self, app):
        self.app = app
        self.event_system = EventSystem()
        self.plugin_loader = PluginLoader(app)

    def run(self):
        collectors = self.plugin_loader.load_plugins(type='collector')
        processors = self.plugin_loader.load_plugins(type='processor')

        collector_system = CollectorSystem(self.event_system, collectors)
        processing_system = ProcessingSystem(self.event_system, processors)

        with ThreadPoolExecutor() as executor:
            executor.submit(collector_system.run_collectors)
            executor.submit(processing_system.run_processors)

        self.event_system.trigger_event('POLL')
