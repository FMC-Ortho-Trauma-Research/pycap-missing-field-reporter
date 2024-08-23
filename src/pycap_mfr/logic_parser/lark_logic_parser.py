from lark import Lark, Transformer

from pycap_mfr.data.config.config import REDCAP_LOGIC_GRAMMAR
from pycap_mfr.logic_parser.logic_parser import LogicParser


class LarkLogicTransformer(Transformer):

    def __init__(self) -> None:
        pass


class LarkLogicParser(LogicParser):

    def __init__(
        self,
        grammar: str = REDCAP_LOGIC_GRAMMAR,
        parser: str = "lalr",
        transformer: Transformer | None = None,
    ) -> None:
        if transformer is None:
            transformer = LarkLogicTransformer()
        self.parser = Lark(grammar, parser=parser, transformer=transformer)

    def evaluate(self, expression: str) -> bool:
        raise NotImplementedError
