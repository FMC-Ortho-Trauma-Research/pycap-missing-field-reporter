import random

import pandas as pd

from pycap_mfr.logic_parser.lark_logic_parser import LarkLogicParser

test_strings = {
    "categorical_eq": (
        "[frailty_score] = '1'",
        "(dff['frailty_score'] == '1')",
    ),
    "numeric_eq": (
        "[num_pushups] = 25",
        "(dff['num_pushups'] == '25')",
    ),
    "gte": (
        "[num_pushups] >= 90",
        "(dff['num_pushups'] >= 90)",
    ),
    "eq_text": (
        "[num_pushups] = '1' and [status] = 'Sick'",
        "((dff['num_pushups'] == '1') & (dff['status'] == 'Sick'))",
    ),
    "categorical_neq": (
        "[frailty_score] <> '2'",
        "(dff['frailty_score'] != '2')",
    ),
    "numeric_neq": (
        "[num_pushups] <> 30",
        "(dff['num_pushups'] != '30')",
    ),
    "parentheses_eq": (
        "([num_pushups] = 25)",
        "(dff['num_pushups'] == '25')",
    ),
    "negation_eq": (
        "!([frailty_score] = '3')",
        "~((dff['frailty_score'] == '3'))",
    ),
    "and_case_lt": (
        "[num_pushups] < 2 AND [bmi] < 30",
        "((dff['num_pushups'] < 2) & (dff['bmi'] < 30))",
    ),
    "and_eq": (
        "[num_pushups] = 25 and [frailty_score] = '4'",
        "((dff['num_pushups'] == '25') & (dff['frailty_score'] == '4'))",
    ),
    "or_case_gt_lte": (
        "[num_pushups] > 30 OR [num_pushups] <= 10",
        "((dff['num_pushups'] > 30) | (dff['num_pushups'] <= 10))",
    ),
    "or_eq": (
        "[num_pushups] = 25 or [frailty_score] = '5'",
        "((dff['num_pushups'] == '25') | (dff['frailty_score'] == '5'))",
    ),
    "or_gt_lt": (
        "[num_pushups] > 75 or [num_pushups] < 30",
        "((dff['num_pushups'] > 75) | (dff['num_pushups'] < 30))",
    ),
    "and_gte_lte": (
        "[num_pushups] >= 25 and [num_pushups] <= 30",
        "((dff['num_pushups'] >= 25) & (dff['num_pushups'] <= 30))",
    ),
    "combined_logical_operators": (
        "[num_pushups] >= 90 and [frailty_score] = '1' or [num_pushups] <= 18 and [frailty_score] = '2'",
        "(((dff['num_pushups'] >= 90) & (dff['frailty_score'] == '1')) | ((dff['num_pushups'] <= 18) & (dff['frailty_score'] == '2')))",
    ),
    "combined_logical_operators_negation_parentheses": (
        "(!([num_pushups] > '2' AND [frailty_score] = '1') OR [num_pushups] < 2) AND [frailty_score] = '1'",
        "((~(((dff['num_pushups'] > 2) & (dff['frailty_score'] == '1'))) | (dff['num_pushups'] < 2)) & (dff['frailty_score'] == '1'))",
    ),
    "term_order_eq": (
        "2 = [num_pushups]",
        "('2' == dff['num_pushups'])",
    ),
    "double_field_reference_eq": (
        "[num_pushups] = [BMI]",
        "(dff['num_pushups'] == dff['BMI'])",
    ),
    "comparison_value_type_missmatch": (
        "[num_pushups] < '2' OR [num_pushups] >= '30' AND [frailty_score] = 1",
        "((dff['num_pushups'] < 2) | ((dff['num_pushups'] >= 30) & (dff['frailty_score'] == '1')))",
    ),
}


def generate_df(num_records: int) -> pd.DataFrame:
    result = []

    for i in range(1, num_records + 1):
        result.extend(list([f"001_{i:03}"] * random.randint(1, 3)))

    dff = pd.DataFrame(
        {
            "record_id": result,
        },
    )

    event_name_dict = {
        1: "baseline_arm_1",
        2: "intra_op_arm_1",
        3: "post_op_arm_1",
    }

    dff["redcap_event_name"] = (dff.groupby("record_id").cumcount() + 1).map(
        event_name_dict
    )
    dff["num_pushups"] = [random.randint(0, 99) for _ in range(len(dff))]
    dff["frailty_score"] = [
        random.choice(["1", "2", "3", "4", "5"]) for _ in range(len(dff))
    ]
    dff["status"] = [
        random.choice(["", "Healthy", "Sick", "Recovered"])
        for _ in range(len(dff))
    ]
    dff["BMI"] = [round(random.uniform(15, 40), 1) for _ in range(len(dff))]

    return dff


def test_lark_logic_parser() -> None:
    lark_parser = LarkLogicParser()
    for test_str, expected in test_strings.values():
        result = lark_parser.translate(test_str)

        assert (
            result == expected
        ), f"\nExpected: {expected}\n     Got: {result}"


if __name__ == "__main__":
    test_lark_logic_parser()
    print("All tests passed!")
