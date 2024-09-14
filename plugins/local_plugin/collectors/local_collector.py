import os
from datetime import datetime
from core.collectors.collector_interface import CollectorInterface
from core.entities.scrap import Scrap

class LocalCollector(CollectorInterface):
    def __init__(self, app):
        self.source = app.make('LocalService')
        self.repository = app.make('PostgresRepository')
        self.event_system = app.make('EventSystem')

    def collect(self):
        scrape_files = self.source.fetch_scrape_files()
        if not scrape_files:
            print("No new files to process.")
            return
        self.process_files(scrape_files)

    def process_files(self, files):
        for file_meta in files:
            self.on_new_file_detected(file_meta)

    def on_new_file_detected(self, file_meta):
        occurrence_time = self._get_file_modification_time(file_meta['file_path'])

        existing_scrap = self.repository.get_scrap_by_filename_and_hash(file_meta['filename'], file_meta['hash'])
        
        if existing_scrap:
            return

        scrap = self.create_scrap(file_meta, occurrence_time)

        scrap_id = self.repository.save_scrap_reference(scrap, state='PROCESSING')
        if scrap_id:
            scrap.id = scrap_id
            print(f"File {file_meta['filename']} is marked as processing with id {scrap_id}.")
            self.event_system.trigger_event('COLLECTED', scrap)
        else:
            print(f"Failed to save scrap for file {file_meta['filename']}.")

    def create_scrap(self, file_meta, occurrence_time):
        creation_time = self._get_file_creation_time(file_meta['file_path'])
        return Scrap(
            hash=file_meta['hash'],
            source='local',
            filename=file_meta['filename'],
            file_path=file_meta['file_path'],
            timestamp=creation_time,
            content=file_meta['content'],
            state='PROCESSING',
            occurrence_time=occurrence_time
        )

    def _get_file_creation_time(self, file_path):
        try:
            return datetime.fromtimestamp(os.path.getctime(file_path))
        except OSError:
            return None

    def _get_file_modification_time(self, file_path):
        try:
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        except OSError:
            return None
