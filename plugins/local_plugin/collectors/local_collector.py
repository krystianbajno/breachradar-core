# plugins/local_plugin/collectors/local_collector.py
import os
from datetime import datetime
from core.collectors.collector_interface import CollectorInterface
from core.entities.scrap import Scrap
from core.events.event_system import EventSystem
from core.repositories.postgres_repository import PostgresRepository
from plugins.local_plugin.services.local_service import LocalService

class LocalCollector(CollectorInterface):
    def __init__(self, app):
        self.source: LocalService = app.make('LocalService')
        self.repository: PostgresRepository = app.make('PostgresRepository')
        self.event_system: EventSystem = app.make('EventSystem')
        self.processed_filenames = set(self.repository.get_processed_filenames())

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
        self.processed_filenames = set(self.repository.get_processed_filenames())
        
        if file_meta["filename"] in self.processed_filenames:
            print(f"File {file_meta['filename']} already processed.")
            return
        
        scrap = self.create_scrap(file_meta, occurrence_time)

        scrap_id = self.repository.save_scrap_reference(scrap, state='PROCESSING')
        if scrap_id:
            scrap.id = scrap_id
            print(f"File {file_meta['filename']} is marked as processing with id {scrap_id}.")
            self.event_system.trigger_event('COLLECTED', scrap)
        else:
            print(f"Failed to save scrap for file {file_meta['filename']}.")
        self.processed_filenames = set(self.repository.get_processed_filenames())

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
