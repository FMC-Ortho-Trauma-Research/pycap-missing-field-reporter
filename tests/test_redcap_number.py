import random

import pandas as pd

from pycap_mfr.redcap_number import RedcapNumber


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
        event_name_dict,
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

def test_convert_df_column(dff: pd.DataFrame, column_name: str) -> pd.Series:
    dff[column_name] = dff[column_name].apply(
        lambda x: RedcapNumber.get_instance(x).num_value,
     )
    return dff[column_name]

if __name__ == "__main__":
    dff = generate_df(10)
    dff = dff.astype(str)

    print(test_convert_df_column(dff, "num_pushups"))
    print(test_convert_df_column(dff, "BMI"))
    print(test_convert_df_column(dff, "frailty_score"))
