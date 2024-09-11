# /plugins/local_plugin/services/local_service.py
import os
import time
import watchdog.events
import watchdog.observers


class LocalService:
    def __init__(self, directory="./data/local_scrapes"):
        self.directory = directory

    def fetch_scrape_files(self):

        scrape_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                scrape_files.append({
                    "file_path": file_path,
                    "filename": file,
                    "size": os.path.getsize(file_path)
                })
        return scrape_files

    def get_file_metadata(self, file_path):
        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path)
        }

    def start_directory_monitor(self, callback):
        event_handler = LocalFileEventHandler(callback)
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, self.directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()


class LocalFileEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path)
