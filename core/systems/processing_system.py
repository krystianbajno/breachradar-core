from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from core.events.event_system import EventSystem

class ProcessingSystem:
    def __init__(self, event_system: EventSystem, processors, repository):
        self.event_system: EventSystem = event_system
        self.processors = processors
        self.repository = repository
        self.executor = ThreadPoolExecutor()
        self.polling_interval = 1

        self.event_system.register_listener('COLLECTED', self.process_scrap)

    def run_processors(self):
        while True:
            try:
                self.executor.submit(self._await_scrap_events)
                self._process_unprocessed_scraps()
            except RuntimeError as e:
                print(f"Error submitting task: {e}")
            time.sleep(self.polling_interval)

    def process_scrap(self, scrap):
        futures = [self.executor.submit(self._run_processor, processor_class, scrap)
                   for processor_class in self.processors]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing scrap: {e}")

    def _run_processor(self, processor, scrap):
        try:
            processor.process(scrap)
        except Exception as e:
            print(f"Error running processor {processor}: {e}")

    def _await_scrap_events(self):
        time.sleep(self.polling_interval)

    def _process_unprocessed_scraps(self):
        scraps = self.repository.get_unprocessed_scraps()

        for scrap in scraps:
            self.process_scrap(scrap)

    def handle(self, entities):
        self.run_processors()
