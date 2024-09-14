from core.repositories.elastic_repository import ElasticRepository
from core.repositories.postgres_repository import PostgresRepository
from core.processors.core_processor import CoreProcessor

class LocalProcessor:
    def __init__(self, app):
        self.repository = app.make('PostgresRepository')
        self.elastic_repository = app.make('ElasticRepository')
        self.core_processor = app.make('CoreProcessor')
        self.event_system = app.make('EventSystem')

        # Register as a listener to the 'COLLECTED' event
        self.event_system.register_listener('COLLECTED', self.process)

    def process(self, scrap):
        try:
            # Check if the scrap already exists in the database
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
                elastic_link = self.elastic_repository.save_scrap(scrap)
                self.repository.update_scrap_with_elastic_link(scrap.id, elastic_link)
            else:
                self.repository.clear_scrap_content(scrap.id)

            self.repository.update_scrap_state(scrap.id, 'PROCESSED')
            print(f"Scrap with id {scrap.id} processed successfully.")

        except Exception as e:
            self.repository.update_scrap_state(scrap.id, 'FAILED')
            print(f"Error processing scrap with id {scrap.id}: {e}")

    def _process_scrap_content(self, scrap):
        """Process the content to check for credentials."""
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
