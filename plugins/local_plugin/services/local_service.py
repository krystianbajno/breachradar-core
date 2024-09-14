import os
import hashlib
import zstandard as zstd
import threading
import time

class LocalService:
    def __init__(self, directory="./data/local_ingest", system_tick=5):
        self.directory = directory
        self.system_tick = system_tick
        self.monitor_thread = None
        self.stop_event = threading.Event()

    def fetch_scrape_files(self):
        scrape_files = []
        try:
            for root, _, files in os.walk(self.directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_meta = self.get_file_metadata(file_path)
                    if file_meta:
                        scrape_files.append(file_meta)
                        
            return scrape_files
        except Exception as e:
            print(f"Error fetching scrape files: {e}")
            return []

    def get_file_metadata(self, file_path):
        try:
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
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def decompress_zstd(self, file_path):
        with open(file_path, 'rb') as compressed_file:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(compressed_file.read())

    @staticmethod
    def calculate_hash(file_content):
        return hashlib.sha256(file_content).hexdigest()

    def start_directory_monitor(self, callback):
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.stop_event.clear()
            self.monitor_thread = threading.Thread(target=self._monitor_directory, args=(callback,))
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print(f"Started monitoring directory: {self.directory} with a refresh interval of {self.system_tick} seconds.")

    def _monitor_directory(self, callback):
        processed_files = set()
        while not self.stop_event.is_set():
            for root, _, files in os.walk(self.directory):
                for file in files:
                    file_path = os.path.join(root, file)

                    if file_path in processed_files:
                        continue

                    file_meta = self.get_file_metadata(file_path)
                    if file_meta:
                        callback(file_meta)
                        processed_files.add(file_path)
            time.sleep(self.system_tick)

    def stop_directory_monitor(self):
        self.stop_event.set()
        if self.monitor_thread is not None:
            self.monitor_thread.join()
            print("Stopped directory monitoring.")
