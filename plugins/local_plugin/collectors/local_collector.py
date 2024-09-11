# /plugins/local_plugin/collectors/local_collector.py
from core.collectors.collector_interface import CollectorInterface
from core.entities.scrap import Scrap
from core.repositories.postgres_repository import PostgresRepository
from plugins.local_plugin.services.local_service import LocalService

class LocalCollector(CollectorInterface):
    def __init__(self, app):
        self.source = LocalService()
        self.repository = app.make(PostgresRepository.__name__)

        # Collect pre-existing files in the directory
        self.collect_existing_files()

        # Start monitoring the directory for new files
        self.start_directory_monitor()

    def collect_existing_files(self):
        """
        Collect files that already exist in the directory on startup.
        """
        scrape_files = self.source.fetch_scrape_files()
        for file_meta in scrape_files:
            if self.file_already_scraped(file_meta['hash']):
                print(f"File {file_meta['filename']} (hash: {file_meta['hash']}) has already been scraped. Skipping.")
                continue

            scrap = Scrap(
                source='local',
                content=file_meta['content'],
                filename=file_meta['filename']
            )
            # Save new scrap reference in the database
            self.repository.save_scrap_reference(scrap, file_meta['file_path'])
            print(f"Pre-existing file {file_meta['filename']} saved to the database.")

    def start_directory_monitor(self):
        """
        Start monitoring the directory for newly added files.
        """
        self.source.start_directory_monitor(self.on_new_file_detected)

    def on_new_file_detected(self, file_path):
        """
        Process newly detected files and save them if they haven't been scraped.
        """
        print(f"Processing new file: {file_path}")

        # Get metadata and content for the new file
        file_meta = self.source.get_file_metadata(file_path)
        if self.file_already_scraped(file_meta['hash']):
            print(f"File {file_meta['filename']} (hash: {file_meta['hash']}) has already been scraped. Skipping.")
            return

        # Create a new scrap object
        scrap = Scrap(
            source='local',
            content=file_meta['content'],
            filename=file_meta['filename']
        )
        # Save the new scrap reference
        self.repository.save_scrap_reference(scrap, file_meta['file_path'])
        print(f"New file {file_meta['filename']} saved to the database.")

    def file_already_scraped(self, file_hash):
        """
        Check if a file with the given hash has already been scraped.
        """
        existing_scrap = self.repository.get_scrap_by_hash(file_hash)
        return existing_scrap is not None
