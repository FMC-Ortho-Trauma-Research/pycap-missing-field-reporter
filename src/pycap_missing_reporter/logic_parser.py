from lark import Lark, Transformer

REDCAP_LOGIC_GRAMMAR = r"""
    start: logic_str

    logic_str: term
        | logic_str AND term -> and_operation
        | logic_str OR term -> or_operation

    term: comparison
        | "(" logic_str ")"

    comparison: categorical_comparison
        | numeric_comparison

    categorical_comparison: field_name "=" categorical_value -> eq
        | field_name "!=" categorical_value -> ne

    numeric_comparison: field_name "=" numeric_value -> eq
                      | field_name "!=" numeric_value -> ne
                      | field_name "<>" numeric_value -> ne
                      | field_name ">" numeric_value -> gt
                      | field_name "<" numeric_value -> lt
                      | field_name ">=" numeric_value -> ge
                      | field_name "<=" numeric_value -> le

    field_name: "[" CNAME "]"

    categorical_value: "'" (CNAME | SIGNED_NUMBER) "'"

    numeric_value: SIGNED_NUMBER
                  | ESCAPED_STRING

    AND: "AND"i
    OR: "OR"i

    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""


class LogicTransformer(Transformer):
    def or_operation(self, args):
        return f"({args[0]}) or ({args[1]})"

    def and_operation(self, args):
        return f"({args[0]}) and ({args[1]})"

    def eq(self, args):
        return f"{args[0]} == {args[1]}"

    def ne(self, args):
        return f"{args[0]} != {args[1]}"

    def gt(self, args):
        return f"{args[0]} > {args[1]}"

    def lt(self, args):
        return f"{args[0]} < {args[1]}"

    def ge(self, args):
        return f"{args[0]} >= {args[1]}"

    def le(self, args):
        return f"{args[0]} <= {args[1]}"

    def field_name(self, args):
        return args[0]

    def categorical_value(self, args):
        return f"'{args[0]}'"

    def numeric_value(self, args):
        return args[0]

    def start(self, args):
        return args[0]


redcap_logic_parser = Lark(
    REDCAP_LOGIC_GRAMMAR, parser="lalr", transformer=LogicTransformer()
)

logic_str = "[num_pushups] >= 90 and [frailty_score] = '1' or [num_pushups] <= 18 and [frailty_score] = '2'"
transformed_logic_str = redcap_logic_parser.parse(logic_str)
print(transformed_logic_str)
