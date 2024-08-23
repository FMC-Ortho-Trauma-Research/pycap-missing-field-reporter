from lark import Lark, Transformer
from pycap_mfr.data.config.config import REDCAP_LOGIC_GRAMMAR
import pandas as pd


class LogicTransformer(Transformer):
    dff = pd.DataFrame(
        {
            "num_pushups": [100, 50, 10, 5, 1],
            "frailty_score": ["1", "2", "1", "2", "1"],
        }
    )
    def or_operation(self, args):
        return f"({args[0]}) or ({args[2]})"

    def and_operation(self, args):
        return f"({args[0]}) and ({args[2]})"

    def eq(self, args):
        return f"{args[0]} == {args[1]}"

    def ne(self, args):
        return f"{args[0]} != {args[1]}"

    def gt(self, args):
        return f"{args[0]} > {args[1]}"

    def lt(self, args):
        return f"{args[0]} < {args[1]}"

    def gte(self, args):
        return f"{args[0]} >= {args[1]}"

    def lte(self, args):
        return f"{args[0]} <= {args[1]}"

    def field_name(self, args):
        return f"{args[0]}"

    def categorical_value(self, args):
        return f"'{args[0]}'"

    def numeric_value(self, args):
        return int(args[0])

    def start(self, args):
        return self.dff.eval(args[0])

    def term(self, args):
        return f"{args[0]}"

    def comparison(self, args):
        return f"{args[0]}"

    def logic_str(self, args):
        return f"{args[0]}"

    def and_term(self, args):
        return f"{args[0]}"


# Initialize the Lark parser with the grammar and transformer
redcap_logic_parser = Lark(
    REDCAP_LOGIC_GRAMMAR, parser="lalr", transformer= LogicTransformer()
)

# Logic string to evaluate
raw_logic_str = "[num_pushups] >= 90 AND [frailty_score] = '1' OR [num_pushups] <= 18 AND [frailty_score] = '2'"

# Parse and transform the logic string
parse_tree = redcap_logic_parser.parse(raw_logic_str)

print(parse_tree)



