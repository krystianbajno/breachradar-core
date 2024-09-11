from core.repositories.elastic_repository import ElasticRepository
from core.components.scrap_component import ScrapComponent
from core.repositories.postgres_repository import PostgresRepository

class LocalProcessor:
    def __init__(self, app):
        self.repository = app.make(PostgresRepository.__name__)
        self.elastic_repository = app.make(ElasticRepository.__name__)

    def process_scrap(self, scrap):
        existing_scrap = self.repository.get_scrap_by_hash(scrap.hash)
        
        if existing_scrap:
            print(f"Scrap with hash {scrap.hash} already exists. Referencing previous scrape.")
            self.repository.reference_existing_scrap(scrap, existing_scrap[0])
        else:
            file_path = self.repository.get_scrap_file_path(scrap.hash)
            with open(file_path, 'r') as f:
                file_content = f.read()

            scrap_component = ScrapComponent(scrap)
            scrap_component.scrap.content = file_content
            self.elastic_repository.save_scrap(scrap_component.scrap)

            self.repository.update_scrap_state(scrap.hash, "PROCESSED")
