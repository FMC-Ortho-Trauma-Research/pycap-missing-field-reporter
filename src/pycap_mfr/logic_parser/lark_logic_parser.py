from lark import Lark, Transformer

from pycap_mfr.data.config.config import STRICT_REDCAP_LOGIC_GRAMMAR
from pycap_mfr.logic_parser.logic_parser import LogicParser


class LarkLogicTransformer(Transformer):

    def __init__(self) -> None:
        return

    def or_term(self, args: list) -> str:
        return f"({args[0]} | {args[1]})"

    def and_term(self, args: list) -> str:
        return f"({args[0]} & {args[1]})"

    def unary_not(self, args: list) -> str:
        return f"~({args[0]})"

    def numeric_comparison(self, args: list) -> str:
        return f"({args[0]} {args[1]} {args[2]})"

    def categorical_comparison(self, args: list) -> str:
        val1, val2 = args[0], args[2]
        val1, val2 = self._format_cat_field_references(val1, val2)
        return f"({val1} {args[1]} {val2})"

    def _format_cat_field_references(self, *args: str) -> tuple[str, ...]:
        return tuple(
            arg if "dff[" in arg else f"'{arg}'" for arg in args
        )

    def field_reference(self, args: list) -> str:
        return f"dff['{args[0]}']"

    def number(self, args: list) -> str:
        return f"{args[0]}"

    def category(self, args: list) -> str:
        return f"{args[0]}"

    def text(self, args: list) -> str:
        return f"{args[0]}"

    def num_operation(self, args: list) -> str:
        return f"{args[0]}"

    def cat_operation(self, args: list) -> str:
        return f"{args[0]}"

    def eq(self, _: list) -> str:
        return "=="

    def ne(self, _: list) -> str:
        return "!="


class LarkLogicParser(LogicParser):

    def __init__(
        self,
        grammar: str = STRICT_REDCAP_LOGIC_GRAMMAR,
        parser: str = "lalr",
        transformer: Transformer | None = None,
    ) -> None:
        if transformer is None:
            transformer = LarkLogicTransformer()
        self.parser = Lark(grammar, parser=parser, transformer=transformer)

    def translate(self, expression: str) -> str:
        expression = self._preprocess_logic_str(expression)
        return str(self.parser.parse(expression))

    def _preprocess_logic_str(self, expression: str) -> str:
        raise NotImplementedError
