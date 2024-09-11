from core.repositories.postgres_repository import PostgresRepository
from core.systems.collector_system import CollectorSystem
from core.systems.processing_system import ProcessingSystem
from core.plugins.plugin_loader import PluginLoader

class AppSystemProvider:
    def __init__(self, app):
        self.app = app
        self.plugin_loader = PluginLoader(app)

    def boot(self):
        postgres_repo = self.app.make(PostgresRepository.__name__)
        event_system = self.app.make('EventSystem')

        self.plugin_loader.load_plugins()

        collectors = self.plugin_loader.get_plugins('collector')
        processors = self.plugin_loader.get_plugins('processor')

        collector_system = CollectorSystem(event_system, collectors)
        processing_system = ProcessingSystem(event_system, processors, postgres_repo)

        self.app.add_system(lambda app: collector_system)
        self.app.add_system(lambda app: processing_system)

    def register(self):
        pass
