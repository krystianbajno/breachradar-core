from core.repositories.elastic_repository import ElasticRepository
from core.repositories.postgres_repository import PostgresRepository
from core.systems.collector_system import CollectorSystem
from core.systems.processing_system import ProcessingSystem

class AppSystemProvider:
    def __init__(self, app):
        self.app = app

    def boot(self):
        postgres_repo = self.app.make(PostgresRepository.__name__)
        elastic_repo = self.app.make(ElasticRepository.__name__)

        self.app.add_system(lambda app: CollectorSystem(
            postgres_repo,
            elastic_repo
        ))

        self.app.add_system(lambda app: ProcessingSystem(
            postgres_repo,
            elastic_repo
        ))
