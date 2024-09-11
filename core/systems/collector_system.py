from concurrent.futures import ThreadPoolExecutor

class CollectorSystem:
    def __init__(self, event_system, collectors):
        self.event_system = event_system
        self.collectors = collectors
        
    def run_collectors(self):
        with ThreadPoolExecutor() as executor:
            for collector in self.collectors:
                executor.submit(self._run_collector, collector)

    def _run_collector(self, collector):
        try:
            scrapes = collector.collect()
            
            for scrap in scrapes:
                self.event_system.trigger_event('SCRAP_COLLECTED', scrap)
                
        except Exception as e:
            print(f"Error running collector {collector}: {e}")

    def handle(self, entities):
        self.run_collectors()
