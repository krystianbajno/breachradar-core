from concurrent.futures import ThreadPoolExecutor
from core.systems.collector_system import CollectorSystem
from core.systems.processing_system import ProcessingSystem

class ECSManager:
    def __init__(self, app):
        self.app = app
        self.event_system = self.app.make('EventSystem')

    def run(self):
        collector_system = self.app.get_system(CollectorSystem.__name__)
        processing_system = self.app.get_system(ProcessingSystem.__name__)

        with ThreadPoolExecutor() as executor:
            executor.submit(collector_system.run_collectors)
            executor.submit(processing_system.run_processors)

        self.event_system.trigger_event('POLL')
