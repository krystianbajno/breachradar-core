from core.repositories.postgres_repository import PostgresRepository
from core.repositories.elastic_repository import ElasticRepository

class AppServiceProvider:
    def __init__(self, app):
        self.app = app

    def register(self):
        self.app.bind(PostgresRepository.__name__, lambda: PostgresRepository(self.app.config()["postgres"]))
        self.app.bind(ElasticRepository.__name__, lambda: ElasticRepository(self.app.config()["elasticsearch"]))
