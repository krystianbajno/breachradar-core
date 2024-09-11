from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirectoryMonitor(FileSystemEventHandler):
    def __init__(self, directory_to_watch, event_callback):
        super().__init__()
        self.directory_to_watch = directory_to_watch
        self.event_callback = event_callback
        self.observer = Observer()

    def on_created(self, event):
        if not event.is_directory:
            print(f"File {event.src_path} has been created.")
            self.event_callback(event.src_path)

    def start(self):
        print(f"Monitoring directory: {self.directory_to_watch}")
        self.observer.schedule(self, self.directory_to_watch, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

