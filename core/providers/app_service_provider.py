from core.events.event_system import EventSystem
from core.repositories.postgres_repository import PostgresRepository
from core.repositories.elastic_repository import ElasticRepository

class AppServiceProvider:
    def __init__(self, app):
        self.app = app

    def register(self):
        postgres_config = self.app.make('config').get_postgres_config()
        self.app.bind('EventSystem', lambda: EventSystem())

        self.app.bind(PostgresRepository.__name__, lambda: PostgresRepository(postgres_config))
        
        elasticsearch_config = self.app.make('config').get_elasticsearch_config()
        self.app.bind(ElasticRepository.__name__, lambda: ElasticRepository(elasticsearch_config))

    def boot(self):
        pass