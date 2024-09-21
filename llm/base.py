from abc import ABC, abstractmethod


class LLMBase(ABC):
    @abstractmethod
    def predict(self, input_query: str) -> dict:
        """This method should be implemented by subclasses."""
        pass

    @abstractmethod
    def add_context(self, user: str, ai: str) -> None:
        """This method should be implemented by subclasses."""
        pass
