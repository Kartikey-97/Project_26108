from abc import ABC, abstractmethod

class ReasoningProvider(ABC):
    @abstractmethod
    def analyze(self, req_text, req_type, standards, is_reference=None, cited_year=None):
        pass
