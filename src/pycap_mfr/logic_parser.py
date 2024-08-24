import pandas as pd
from lark import Lark, Transformer, Token

from pycap_mfr.data.config.config import (
    REDCAP_LOGIC_GRAMMAR,
    STRICT_REDCAP_LOGIC_GRAMMAR,
 )


class RedcapLogicTransformer(Transformer):

    def field_reference(self, items):
        return f"dff['{items[0]}']"

    def num_operation(self, items):
        return f"{items[0]}"

    def cat_operation(self, items):
        return f"{items[0]}"

    def numeric_comparison(self, items):
        return f"({items[0]} {items[1]} {items[2]})"

    def categorical_comparison(self, items):
        val = items[2]
        if "dff['" not in val:
            val = f"'{val}'"
        return f"({items[0]} {items[1]} {val})"

    def and_term(self, items):
        return f"({items[0]} & {items[1]})"

    def or_term(self, items):
        return f"({items[0]} | {items[1]})"

    def unary_not(self, items):
        return f"~({items[0]})"

    def number(self, items):
        return f"{items[0]}"

    def category(self, items):
        return f"{items[0]}"

    def text(self, items):
        return f"{items[0]}"

    def eq(self, _):
        return "=="

    def ne(self, _):
        return "!="

# Initialize the Lark parser with the grammar and transformer
redcap_logic_parser = Lark(
    STRICT_REDCAP_LOGIC_GRAMMAR,
    parser="lalr",
    transformer=RedcapLogicTransformer(),
)

# Logic string to evaluate
test1 = "[num_pushups] >= 90"
test2 = "[num_pushups] = 1 and [sex] = 'Male'"
test3 = "[num_pushups] < 2 AND [health_status] = '1'"
test4 = "[num_pushups] < 2 OR [num_pushups] >= 30"
test5 = "[num_pushups] < 2 OR [num_pushups] >= 30 AND [health_status] = '1'"
test6 = "([num_pushups] < 2 OR [num_pushups] >= 30) AND [health_status] = '1'"
test7 = "2 = [num_pushups]"
test8 = "!([num_pushups]  2)"
test9 = "(!([num_pushups] > '2' AND [health_status] = '1') OR [num_pushups] < 2) AND [health_status] = '1'"
test10 = "[num_pushups] < '2' OR [num_pushups] >= '30' AND [health_status] = 1"
test11 = "[num_pushups] >= (22 or 30)"

# Parse and transform the logic string
parse_tree = redcap_logic_parser.parse(test11).pretty()

print(parse_tree)



