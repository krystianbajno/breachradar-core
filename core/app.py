from threading import Thread
from typing import Callable

class App:
    def __init__(self):
        self.configuration = None
        self.providers = []
        self.services = {}
        self.systems = []
        self.entities = {}

    def add_system(self, function):
        self.systems.append(function(self))

    def get_system(self, system_name):
        for system in self.systems:
            if system.__class__.__name__ == system_name:
                return system
        raise ValueError(f"System '{system_name}' not found.")

    def add_entity(self, function: Callable):
        entity = function(self)
        self.entities[entity.get_id()] = entity

    def get_entity_by_id(self, identifier):
        return self.entities.get(identifier)

    def register(self, provider_class):
        provider = provider_class(self)
        provider.register()
        self.providers.append(provider)

    def bind(self, interface, function: Callable, lazy=False):
        if lazy:
            self.services[interface] = function
        else:
            self.services[interface] = function()

    def make(self, name):
        if name not in self.services:
            raise ValueError(f"Service '{name}' not registered.")
        if callable(self.services[name]):
            return self.services[name]()
        return self.services[name]

    def boot(self):
        for provider in self.providers:
            provider.boot()

    def run_systems(self, tick: Callable):
        def run_system(system):
            while True:
                system.handle(self.entities)
                tick(self.entities)

        for system in self.systems:
            thread = Thread(target=run_system, args=[system])
            thread.start()
