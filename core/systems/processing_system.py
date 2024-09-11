from concurrent.futures import ThreadPoolExecutor, as_completed

class ProcessingSystem:
    def __init__(self, event_system, processors, repository):
        self.event_system = event_system
        self.processors = processors
        self.repository = repository
        self.executor = ThreadPoolExecutor()
        self.event_system.register_listener('SCRAP_COLLECTED', self.process_scrap)

    def run_processors(self):
        self.executor.submit(self._await_scrap_events)

    def process_scrap(self, scrap):
        futures = [self.executor.submit(self._run_processor, processor_class, scrap)
                   for processor_class in self.processors]

        for future in as_completed(futures):
            try:
                future.result()  
            except Exception as e:
                print(f"Error in processing scrap: {e}")

    def _run_processor(self, processor_class, scrap):
        processor = processor_class(self.event_system)
        processor.process(scrap)
        self.repository.update_scrap_state(scrap.hash, "SCRAP_PROCESSED")

    def _await_scrap_events(self):
        pass
