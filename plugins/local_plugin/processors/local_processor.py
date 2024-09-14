from core.repositories.elastic_repository import ElasticRepository
from core.repositories.postgres_repository import PostgresRepository
from core.processors.core_processor import CoreProcessor
from core.entities.elastic_chunk import ElasticChunk

class LocalProcessor:
    def __init__(self, app):
        self.repository: PostgresRepository = app.make('PostgresRepository')
        self.elastic_repository: ElasticRepository = app.make('ElasticRepository')
        self.core_processor: CoreProcessor = app.make('CoreProcessor')
        self.event_system = app.make('EventSystem')

        self.event_system.register_listener('COLLECTED', self.process)

    def process(self, scrap):
        try:
            existing_scrap = self.repository.get_scrap_by_id(scrap.id)
            if not existing_scrap:
                print(f"Scrap with id {scrap.id} does not exist in the database. Skipping.")
                return

            if existing_scrap.state in ['PROCESSED']:
                print(f"Scrap with id {scrap.id} is in state {existing_scrap.state}. Skipping.")
                return

            if existing_scrap.state == 'FAILED':
                self.repository.update_scrap_state(scrap.id, 'PROCESSING')

            print(f"Processing scrap with id {scrap.id}.")

            credentials_found = self._process_scrap_content(scrap)

            if credentials_found:
                self._save_chunks_to_elasticsearch(scrap)
            else:
                self.repository.clear_scrap_content(scrap.id)

            self.repository.update_scrap_state(scrap.id, 'PROCESSED')
            print(f"Scrap with id {scrap.id} processed successfully.")

        except Exception as e:
            self.repository.update_scrap_state(scrap.id, 'FAILED')
            print(f"Error processing scrap with id {scrap.id}: {e}")

    def _process_scrap_content(self, scrap):
        try:
            file_content = scrap.content.decode('utf-8', errors='replace')
        except AttributeError:
            print(f"Invalid content format for scrap {scrap.id}. Skipping processing.")
            return False

        credentials = self.core_processor.check_for_credentials(file_content)
        if credentials:
            scrap.content = file_content
            return True
        return False

    def _save_chunks_to_elasticsearch(self, scrap):
        content = scrap.content
        chunk_size = 1000000 
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
        
        elastic_ids = []
        for index, chunk in enumerate(chunks):
            elastic_chunk = ElasticChunk(scrap_id=scrap.id, chunk_number=index + 1, chunk_content=chunk)
            elastic_id = self.elastic_repository.save_scrap_chunk(elastic_chunk)
            self.repository.save_elastic_chunk(
                scrap.id,
                elastic_chunk.chunk_number,
                elastic_id
            )
            elastic_ids.append(elastic_id)
        
        return elastic_ids