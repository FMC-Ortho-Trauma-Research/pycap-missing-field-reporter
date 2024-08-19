import random

import pandas as pd

categorical_eq = "[frailty_score] = '1'"
numeric_eq = "[num_pushups] = 25"
categorical_neq = "[frailty_score] != '2'"
numeric_neq = "[num_pushups] <> 30"
parentheses_eq = "([num_pushups] = 25)"
negation_eq = "!([frailty_score] = '3')"
and_eq = "[num_pushups] = 25 and [frailty_score] = '4'"
or_eq = "[num_pushups] = 25 or [frailty_score] = '5'"
or_gt_lt = "[num_pushups] > 75 or [num_pushups] < 30"
and_gte_lte = "[num_pushups] >= 25 and [num_pushups] <= 30"
combined_logical_operators = "[num_pushups] >= 90 and [frailty_score] = '1' or [num_pushups] <= 18 and [frailty_score] = '2'"

num_records = 250

def generate_df(num_records):
    result = []

    for i in range(1, num_records + 1):
        result.extend([id for id in ([f"001_{i:03}"] * random.randint(1, 3))])

    df = pd.DataFrame(
        {
            "record_id": result
        }
    )

    event_name_dict = {
        1: "baseline_arm_1",
        2: "intra_op_arm_1",
        3: "post_op_arm_1",
    }

    df["redcap_event_name"] = (df.groupby("record_id").cumcount() + 1).map(event_name_dict)
    df["num_pushups"] = [random.randint(0, 99) for _ in range(len(df))]
    df["frailty_score"] = [random.choice(['1', '2', '3', '4', '5']) for _ in range(len(df))]
    df["status"] = [random.choice(["", "Healthy", "Sick", "Recovered"]) for _ in range(len(df))]
    df["BMI"] = [round(random.uniform(15, 40), 1) for _ in range(len(df))]

    return df

