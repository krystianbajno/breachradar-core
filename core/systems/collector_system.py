from concurrent.futures import ThreadPoolExecutor

class CollectorSystem:
    def __init__(self, event_system, collectors):
        self.event_system = event_system
        self.collectors = collectors

    def run_collectors(self):
        with ThreadPoolExecutor() as executor:
            for collector_class in self.collectors:
                executor.submit(self._run_collector, collector_class)

    def _run_collector(self, collector_class):
        collector = collector_class(self.event_system)
        scrapes = collector.collect()
        for scrap in scrapes:
            self.event_system.trigger_event('SCRAP_COLLECTED', scrap)
