import os
import hashlib
import zstandard as zstd
import time
import watchdog.events
import watchdog.observers
import threading

class LocalService:
    def __init__(self, directory="./data/local_ingest"):
        self.directory = directory
        self.monitor_thread = None

    def fetch_scrape_files(self):
        scrape_files = []
        for root, _, files in os.walk(self.directory):
            print(root,files)
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.zst'):
                    file_content = self.decompress_zstd(file_path)
                else:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()

                file_hash = self.calculate_hash(file_content)

                scrape_files.append({
                    "file_path": file_path,
                    "filename": file,
                    "size": len(file_content),
                    "content": file_content,
                    "hash": file_hash
                })
        return scrape_files

    def get_file_metadata(self, file_path):
        if file_path.endswith('.zst'):
            file_content = self.decompress_zstd(file_path)
        else:
            with open(file_path, 'rb') as f:
                file_content = f.read()

        file_hash = self.calculate_hash(file_content)

        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "size": len(file_content),
            "content": file_content,
            "hash": file_hash
        }

    def decompress_zstd(self, file_path):
        with open(file_path, 'rb') as compressed_file:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(compressed_file.read())

    def calculate_hash(self, file_content):
        return hashlib.sha256(file_content).hexdigest()

    def start_directory_monitor(self, callback):
        """Start directory monitoring in a separate thread."""
        event_handler = LocalFileEventHandler(callback)
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, self.directory, recursive=False)
        
        self.monitor_thread = threading.Thread(target=self._run_monitor, args=(observer,))
        self.monitor_thread.daemon = True  # Set as a daemon thread so it doesn't block the program from exiting
        self.monitor_thread.start()

    def _run_monitor(self, observer):
        """Method to start and run the observer loop in the background."""
        observer.start()
        print(f"Started monitoring directory: {self.directory}")

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
