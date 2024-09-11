from threading import Thread
from typing import Callable

class App:
    configuration = {}
    providers = []
    services = {}
    systems = []
    entities = {}

    def add_entity(self, function: Callable):
        entity = function(self)
        self.entities[entity.get_id()] = entity

    def get_entity_by_id(self, identifier):
        return self.entities.get(identifier)

    def add_system(self, function: Callable):
        self.systems.append(function(self))

    def register(self, provider_class):
        provider = provider_class(self)
        provider.register()
        self.providers.append(provider)

    def configure(self, name, config):
        self.configuration[name] = config

    def config(self):
        return self.configuration

    def bind(self, interface, function: Callable, lazy=False):
        if lazy:
            self.services[interface] = function
        else:
            self.services[interface] = function()

    def make(self, name):
        if name not in self.services:
            raise ValueError(f"Service '{name}' not registered")
        if callable(self.services[name]):
            return self.services[name]()
        return self.services[name]

    def run_systems(self, tick: Callable):
        """
        Run all systems in parallel and invoke the tick function for periodic tasks.
        """
        def run_system(system):
            while True:
                system.handle(self.entities)
                tick(self.entities)

        for system in self.systems:
            thread = Thread(target=run_system, args=[system])
            thread.start()

    def boot(self):
        """
        Boot all providers to ensure all services and systems are ready.
        """
        for provider in self.providers:
            provider.boot()
