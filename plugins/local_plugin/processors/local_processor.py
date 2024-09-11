from core.repositories.elastic_repository import ElasticRepository
from core.components.scrap_component import ScrapComponent
from core.repositories.postgres_repository import PostgresRepository
from core.processors.core_processor import CoreProcessor

class LocalProcessor:
    def __init__(self, app):
        self.repository = app.make(PostgresRepository.__name__)
        self.elastic_repository = app.make(ElasticRepository.__name__)
        self.core_processor = app.make('CoreProcessor')

    def process(self, scrap):
        existing_scrap = self.repository.get_scrap_by_hash(scrap.hash)

        if existing_scrap:
            existing_scrap_state = existing_scrap.state

            if existing_scrap_state == "SCRAP_PROCESSED":
                print(f"Scrap with hash {scrap.hash} has already been processed. Skipping.")
                return

            print(f"Scrap with hash {scrap.hash} already exists but is not processed. Processing the scrap.")
            self._process_scrap_content(scrap)
        else:
            print(f"Scrap with hash {scrap.hash} does not exist. Creating and processing the scrap.")
            self._process_scrap_content(scrap)

    def _process_scrap_content(self, scrap):
        file_path = scrap.file_path
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()

            credentials = self.core_processor.check_for_credentials(file_content)
            if credentials:
                print(f"Credentials found in scrap {scrap.hash}: {credentials}")

                scrap_component = ScrapComponent(scrap)
                scrap_component.scrap.content = file_content
                
                try:
                    self.elastic_repository.save_scrap(scrap_component.scrap)
                    self.repository.update_scrap_state(scrap.hash, "SCRAP_PROCESSED")
                    print(f"Scrap with hash {scrap.hash} processed successfully.")
                except Exception as e:
                    print(f"Error saving scrap {scrap.hash} to Elastic: {e}, aborting.")
            else:
                print(f"No credentials found in scrap {scrap.hash}. Not saving to Elasticsearch.")
                self.repository.update_scrap_state(scrap.hash, "SCRAP_PROCESSED")

        except FileNotFoundError:
            print(f"File for scrap with hash {scrap.hash} not found at {file_path}.")
        except Exception as e:
            print(f"Error processing scrap with hash {scrap.hash}: {e}")
