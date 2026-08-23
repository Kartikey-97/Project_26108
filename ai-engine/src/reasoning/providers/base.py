from abc import ABC, abstractmethod

class ReasoningProvider(ABC):
    @abstractmethod
    def analyze(self, req_text, req_type, standards):
        pass
