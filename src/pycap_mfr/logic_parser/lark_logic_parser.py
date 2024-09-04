import re

from lark import Lark, Transformer

from pycap_mfr.data.config.config import (
    FIELD_REFERENCE_LIT,
    STRICT_REDCAP_LOGIC_GRAMMAR,
)
from pycap_mfr.logic_parser.logic_parser import LogicParser


class LarkLogicTransformer(Transformer):
    _patt: re.Pattern = re.compile(FIELD_REFERENCE_LIT)

    def __init__(self) -> None:
        self._field_references = set()

    def get_field_references(self) -> set[str]:
        return self._field_references

    def or_term(self, args: list) -> str:
        return f"({args[0]} | {args[1]})"

    def and_term(self, args: list) -> str:
        return f"({args[0]} & {args[1]})"

    def unary_not(self, args: list) -> str:
        return f"~({args[0]})"

    def numeric_comparison(self, args: list) -> str:
        self._cache_numeric_field_references(args[0], args[2])
        return f"({args[0]} {args[1]} {args[2]})"

    def _cache_numeric_field_references(self, *args: str) -> None:
        for arg in args:
            matches = re.findall(self._patt, arg)
            for match in matches:
                self._field_references.add(match)

    def categorical_comparison(self, args: list) -> str:
        val1, val2 = args[0], args[2]
        val1, val2 = self._format_cat_field_references(val1, val2)
        return f"({val1} {args[1]} {val2})"

    def _format_cat_field_references(self, *args: str) -> tuple[str, ...]:
        return tuple(arg if "dff[" in arg else f"'{arg}'" for arg in args)

    def field_reference(self, args: list) -> str:
        return f"dff['{args[0]}']"

    def number(self, args: list) -> str:
        return f"{args[0]}"

    def category(self, args: list) -> str:
        return f"{args[0]}"

    def text(self, args: list) -> str:
        return f"{args[0]}"

    def none(self, _: list) -> str:
        return ""

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
        transformer: Transformer | LarkLogicTransformer | None = None,
    ) -> None:
        if transformer is None:
            transformer = LarkLogicTransformer()
        self._transformer = transformer
        self._parser = Lark(grammar, parser=parser, transformer=transformer)

    def translate(self, expression: str) -> str:
        expression = self._preprocess_logic_str(expression)
        return str(self.parser.parse(expression))

    def get_field_references(self) -> set[str]:
        if not isinstance(self.transformer, LarkLogicTransformer):
            err_str = "Undefined method for chosen Transformer class."
            raise TypeError(err_str)
        return self.transformer.get_field_references()

    @property
    def parser(self) -> Lark:
        return self._parser

    @property
    def transformer(self) -> LarkLogicTransformer | Transformer:
        return self._transformer

    def _preprocess_logic_str(self, expression: str) -> str:
        expression = expression.replace('"', "'")  # Unify str delimiters
        expression = expression.replace("!=", "<>")  # Unify neq operators

        return expression  # NOQA: RET504
