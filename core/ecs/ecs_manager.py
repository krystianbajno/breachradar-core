from concurrent.futures import ThreadPoolExecutor
from core.app import App
from core.events.event_system import EventSystem
from core.systems.collector_system import CollectorSystem
from core.systems.processing_system import ProcessingSystem
import time

class ECSManager:
    def __init__(self, app: App):
        self.app: App = app
        self.event_system: EventSystem = self.app.make('EventSystem')

    def run(self):
        collector_system = self.app.get_system(CollectorSystem.__name__)
        processing_system = self.app.get_system(ProcessingSystem.__name__)

        with ThreadPoolExecutor() as executor:
            executor.submit(self._run_collectors, collector_system)
            executor.submit(self._run_processors, processing_system)

        self.event_system.trigger_event('POLL')

    def _run_collectors(self, collector_system):
        """Continuously run collectors in a loop with polling interval."""
        while True:
            try:
                collector_system.run_collectors()
            except Exception as e:
                print(f"Error running collectors: {e}")
            time.sleep(1)

    def _run_processors(self, processing_system):
        """Continuously run processors in a loop with polling interval."""
        while True:
            try:
                processing_system.run_processors()
            except Exception as e:
                print(f"Error running processors: {e}")
            time.sleep(1)
