from core.events.event_system import EventSystem
from core.repositories.postgres_repository import PostgresRepository
from core.repositories.elastic_repository import ElasticRepository
from core.processors.core_processor import CoreProcessor

class AppServiceProvider:
    def __init__(self, app):
        self.app = app

    def register(self):
        elasticsearch_config = self.app.make('config').get_elasticsearch_config()

        self.app.bind('EventSystem', lambda: EventSystem())

        self.app.bind(ElasticRepository.__name__, lambda: ElasticRepository(elasticsearch_config))

        self.app.bind(CoreProcessor.__name__, lambda: CoreProcessor(self.app.make(PostgresRepository.__name__)))

    def boot(self):
        pass
