from core.collectors.collector_interface import CollectorInterface
from core.entities.scrap import Scrap
from core.repositories.postgres_repository import PostgresRepository
from plugins.local_plugin.services.local_service import LocalService

class LocalCollector(CollectorInterface):
    def __init__(self, app):
        self.source = LocalService()
        self.repository = app.make(PostgresRepository.__name__)

    def collect(self):
        scrape_files = self.source.fetch_scrape_files()
        self.start_directory_monitor()
        scrapes = []

        for file_meta in scrape_files:
            if self.file_already_scraped(file_meta['hash']):
                print(f"File {file_meta['filename']} (hash: {file_meta['hash']}) has already been scraped. Skipping.")
                continue

            scrap = Scrap(
                source='local',
                content=file_meta['content'],
                filename=file_meta['filename'],
                file_path=file_meta["file_path"]
            )
            
            scrapes.append(scrap)

            self.repository.save_scrap_reference(scrap, file_meta['file_path'])
            print(f"Pre-existing file {file_meta['filename']} saved to the database.")
            
        return scrapes
    
    def start_directory_monitor(self):
        self.source.start_directory_monitor(self.on_new_file_detected)

    def on_new_file_detected(self, file_path):
        print(f"Processing new file: {file_path}")

        file_meta = self.source.get_file_metadata(file_path)
        if self.file_already_scraped(file_meta['hash']):
            print(f"File {file_meta['filename']} (hash: {file_meta['hash']}) has already been scraped. Skipping.")
            return

        scrap = Scrap(
            source='local',
            content=file_meta['content'],
            filename=file_meta['filename'],
            file_path=file_meta["file_path"]
        )

        self.repository.save_scrap_reference(scrap, file_meta['file_path'])
        print(f"New file {file_meta['filename']} saved to the database.")

    def file_already_scraped(self, file_hash):
        existing_scrap = self.repository.get_scrap_by_hash(file_hash)
        return existing_scrap is not None
