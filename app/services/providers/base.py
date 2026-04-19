from abc import ABC, abstractmethod

class TelemetryProvider(ABC):
    @abstractmethod
    def start(self):
        ...
    @abstractmethod
    def stop(self):
        ...
    @abstractmethod
    def register_callback(self, callback):
        ...
    @property
    @abstractmethod
    def status(self):
        ...
