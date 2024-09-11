# /plugins/local_plugin/services/local_service.py
import os
import hashlib
import zstandard as zstd
import time
import watchdog.events
import watchdog.observers


class LocalService:
    def __init__(self, directory="./data/local_scrapes"):
        self.directory = directory

    def fetch_scrape_files(self):
        """
        Fetch files from the directory, decompress if ZSTD compressed, and calculate their hash.
        """
        scrape_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.zst'):
                    # Decompress ZSTD compressed file
                    file_content = self.decompress_zstd(file_path)
                else:
                    # Read normal file
                    with open(file_path, 'rb') as f:
                        file_content = f.read()

                # Calculate the file hash (SHA-256)
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
        """
        Get metadata and content for a single file, decompress if needed.
        """
        if file_path.endswith('.zst'):
            # Decompress ZSTD compressed file
            file_content = self.decompress_zstd(file_path)
        else:
            # Read normal file
            with open(file_path, 'rb') as f:
                file_content = f.read()

        # Calculate the file hash (SHA-256)
        file_hash = self.calculate_hash(file_content)

        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "size": len(file_content),
            "content": file_content,
            "hash": file_hash
        }

    def decompress_zstd(self, file_path):
        """Decompress a ZSTD compressed file and return its content."""
        with open(file_path, 'rb') as compressed_file:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(compressed_file.read())

    def calculate_hash(self, file_content):
        """Calculate the SHA-256 hash of the given file content."""
        return hashlib.sha256(file_content).hexdigest()

    def start_directory_monitor(self, callback):
        """Monitor the directory for new files."""
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
