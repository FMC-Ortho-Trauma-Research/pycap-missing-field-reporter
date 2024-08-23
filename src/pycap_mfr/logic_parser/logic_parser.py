from abc import ABC, abstractmethod


class LogicParser(ABC):

    @abstractmethod
    def evaluate(self, expression: str) -> bool | str:
        raise NotImplementedError
