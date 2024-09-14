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
                self.repository.clear_scrap_content(scrap.id)

                return

            if existing_scrap.state == 'FAILED':
                self.repository.update_scrap_state(scrap.id, 'PROCESSING')

            print(f"Processing scrap with id {scrap.id}.")

            credentials_found = self._process_scrap_content(scrap)

            if credentials_found:
                self._save_chunks_to_elasticsearch(scrap)
                self.repository.clear_scrap_content(scrap.id)

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
        """Will save chunks, but keep whole lines"""
        content = scrap.content
        chunk_size = 1000000  # 1MB chunk size
        elastic_ids = []
        current_chunk = []
        current_chunk_size = 0

        def save_current_chunk():
            """Saves the current chunk to Elasticsearch and resets the chunk state."""
            if current_chunk:  # Only save if there's content
                chunk_content = ''.join(current_chunk)
                chunk_number = len(elastic_ids) + 1
                elastic_chunk = ElasticChunk(scrap_id=scrap.id, chunk_number=chunk_number, chunk_content=chunk_content)
                elastic_id = self.elastic_repository.save_scrap_chunk(elastic_chunk)
                self.repository.save_elastic_chunk(scrap.id, chunk_number, elastic_id)
                elastic_ids.append(elastic_id)

        for line in content.splitlines(keepends=True):  # Keep line breaks for full line chunks
            line_size = len(line.encode('utf-8'))

            # If adding the line exceeds the chunk size, save the current chunk first
            if current_chunk_size + line_size > chunk_size:
                save_current_chunk()
                current_chunk, current_chunk_size = [], 0  # Reset for the next chunk

            # Add the line to the current chunk
            current_chunk.append(line)
            current_chunk_size += line_size

        # Save any remaining content in the last chunk
        save_current_chunk()

        return elastic_ids
