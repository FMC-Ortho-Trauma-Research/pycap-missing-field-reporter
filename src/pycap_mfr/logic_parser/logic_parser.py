from abc import ABC, abstractmethod


class LogicParser(ABC):

    @abstractmethod
    def translate(self, expression: str) -> str:
        raise NotImplementedError
