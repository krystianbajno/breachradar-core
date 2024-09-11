from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ProcessingSystem:
    def __init__(self, event_system, processors, repository):
        self.event_system = event_system
        self.processors = processors
        self.repository = repository
        self.executor = ThreadPoolExecutor()
        self.polling_interval = 1

        self.event_system.register_listener('SCRAP_COLLECTED', self.process_scrap)

    def run_processors(self):
        while True:
            try:
                self.executor.submit(self._await_scrap_events)
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

    def _run_processor(self, processor_class, scrap):
        try:
            processor = processor_class(self.event_system)
            processor.process(scrap)
            self.repository.update_scrap_state(scrap.hash, "SCRAP_PROCESSED")
        except Exception as e:
            print(f"Error running processor {processor_class}: {e}")

    def _await_scrap_events(self):
        time.sleep(self.polling_interval)

    def handle(self, entities):
        self.run_processors()
