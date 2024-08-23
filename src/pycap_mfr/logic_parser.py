import pandas as pd
from lark import Lark, Transformer

from pycap_mfr.data.config.config import (
    REDCAP_LOGIC_GRAMMAR,
    STRICT_REDCAP_LOGIC_GRAMMAR,
 )

# Initialize the Lark parser with the grammar and transformer
redcap_logic_parser = Lark(
    STRICT_REDCAP_LOGIC_GRAMMAR,
    parser="lalr",
    start="redcap_logic_string",
)

# Logic string to evaluate
raw_logic_str = "[num_pushups] >= 90 AND [frailty_score] = '1' OR [num_pushups] <= 18 AND [frailty_score] = '2'"

# Parse and transform the logic string
parse_tree = redcap_logic_parser.parse(raw_logic_str).pretty()

print(parse_tree)



