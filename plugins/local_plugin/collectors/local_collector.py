import os
import time
from core.collectors.collector_interface import CollectorInterface
from core.entities.scrap import Scrap
import hashlib

class LocalCollector(CollectorInterface):
    def __init__(self, app):
        self.source = app.make('LocalService')
        self.repository = app.make('PostgresRepository')
        self.start_directory_monitor()

    def collect(self):
        scrape_files = self.source.fetch_scrape_files()
        return self.process_files(scrape_files)

    def start_directory_monitor(self):
        self.source.start_directory_monitor(self.on_new_file_detected)

    def on_new_file_detected(self, file_path):
        print(f"Processing new file: {file_path}")
        file_meta = self.source.get_file_metadata(file_path)
        self.process_files([file_meta])

    def process_files(self, files):
        """Process a list of files and save them if they haven't been scraped already."""
        scrapes = []
        for file_meta in files:
            if self.file_already_scraped(file_meta['hash']):
                print(f"File {file_meta['filename']} (hash: {file_meta['hash']}) has already been scraped. Skipping.")
                continue

            scrap = self.create_scrap(file_meta)
            scrapes.append(scrap)

            self.repository.save_scrap_reference(scrap, file_meta['file_path'])
            print(f"File {file_meta['filename']} saved to the database.")

        return scrapes

    def create_scrap(self, file_meta):
        """Create a Scrap object and hash its content."""
        file_hash = self.hash_content(file_meta['content'])
        creation_time = self._get_file_creation_time(file_meta['file_path'])

        return Scrap(
            source='local',
            content=file_meta['content'],
            filename=file_meta['filename'],
            file_path=file_meta["file_path"],
            timestamp=creation_time,
            hash=file_hash
        )

    def file_already_scraped(self, file_hash):
        """Check if a file with the given hash has already been scraped."""
        existing_scrap = self.repository.get_scrap_by_hash(file_hash)
        return existing_scrap is not None

    @staticmethod
    def hash_content(content):
        """Hash the content using SHA-256."""
        return hashlib.sha256(content).hexdigest()

    def _get_file_creation_time(self, file_path):
        """Get the creation time of the file."""
        try:
            return time.ctime(os.path.getctime(file_path))
        except OSError:
            return None