from concurrent.futures import ThreadPoolExecutor

from core.events.event_system import EventSystem

class CollectorSystem:
    def __init__(self, event_system: EventSystem, collectors):
        self.event_system: EventSystem = event_system
        self.collectors = collectors
        
    def run_collectors(self):
        with ThreadPoolExecutor() as executor:
            for collector in self.collectors:
                executor.submit(self._run_collector, collector)

    def _run_collector(self, collector):
        try:
            scrapes = collector.collect()
            
            if not scrapes:
                return
            
            for scrap in scrapes:
                self.event_system.trigger_event('COLLECTED', scrap)
                
        except Exception as e:
            print(f"Error running collector {collector}: {e}")

    def handle(self, entities):
        self.run_collectors()
