from abc import ABC, abstractmethod

class CollectorInterface(ABC):
    @abstractmethod
    def collect(self):
        pass
