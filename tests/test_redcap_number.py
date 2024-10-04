from typing import NamedTuple

import numpy as np
import pandas as pd
import pytest
from dateutil.parser import parse

from dqm.redcap_number import RedcapNumber


class TestInput(NamedTuple):
    test_case: str
    test_input: str
    expected_str_val: str
    expected_num_val: float

missing = TestInput("missing", "", "", 0.0)
missing_code = TestInput("missing_code", "NA-2", "NA-2", np.nan)
date = TestInput("date", "2024-09-20", "2024-09-20", np.nan)
category = TestInput("category", "2", "2", 2.0)
numeric = TestInput("numeric", "23.6", "23.6", 23.6)


@pytest.fixture(
    params=[missing, missing_code, date, category, numeric],
    ids=["missing", "missing_code", "date", "category", "numeric"],
)
def test_input(request: pytest.FixtureRequest) -> TestInput:
    return request.param


@pytest.fixture
def test_input_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "category": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "category_missing": ["1", "", "3", "4", "NA-1", "6", "7", " ", "9", "NA-2"],
            "numeric": ["1", "2.2", "3.45", "3.14", "5", "66", "-7.7", "2", "9.001", "10"],
            "numeric_missing": ["1", "", "3.45", "3.14", "NA", "66", "7.7", " ", "9.001", "NA-2"],
            "date_ymd": ["2024-10-1", "2024-10-2", "2024-10-3", "2024-10-4", "2024-10-5", "2024-10-6", "2024-10-7", "2024-10-8", "2024-10-9", "2024-10-10"],
            "dt_ymd_hm": ["2024-10-1 13:23", "2024-10-2 02:33", "2024-10-3 10:00", "2024-10-4 09:10", "2024-10-5 08:02", "2024-10-6 00:00", "2024-10-7 00:32", "2024-10-8 00:50", "2024-10-9 21:50", "2024-10-10 23:59"],
            "dt_ymd_hms": ["2024-10-1 13:23:45", "2024-10-2 02:33:45", "2024-10-3 10:00:00", "2024-10-4 09:10:00", "2024-10-5 08:02:00", "2024-10-6 00:00:00", "2024-10-7 00:32:00", "2024-10-8 00:50:00", "2024-10-9 21:50:00", "2024-10-10 23:59:00"],
            "date_dmy": ["1-10-2024", "2-10-2024", "3-10-2024", "4-10-2024", "5-10-2024", "6-10-2024", "7-10-2024", "8-10-2024", "9-10-2024", "10-10-2024"],
            "dt_dmy_hm": ["1-10-2024 13:23", "2-10-2024 02:33", "3-10-2024 10:00", "4-10-2024 09:10", "5-10-2024 08:02", "6-10-2024 00:00", "7-10-2024 00:32", "8-10-2024 00:50", "9-10-2024 21:50", "10-10-2024 23:59"],
            "dt_dmy_hms": ["1-10-2024 13:23:45", "2-10-2024 02:33:45", "3-10-2024 10:00:00", "4-10-2024 09:10:00", "5-10-2024 08:02:00", "6-10-2024 00:00:00", "7-10-2024 00:32:00", "8-10-2024 00:50:00", "9-10-2024 21:50:00", "10-10-2024 23:59:00"],
            "date_mdy": ["10-1-2024", "10-2-2024", "10-3-2024", "10-4-2024", "10-5-2024", "10-6-2024", "10-7-2024", "10-8-2024", "10-9-2024", "10-10-2024"],
            "dt_mdy_hm": ["10-1-2024 13:23", "10-2-2024 02:33", "10-3-2024 10:00", "10-4-2024 09:10", "10-5-2024 08:02", "10-6-2024 00:00", "10-7-2024 00:32", "10-8-2024 00:50", "10-9-2024 21:50", "10-10-2024 23:59"],
            "dt_mdy_hms": ["10-1-2024 13:23:45", "10-2-2024 02:33:45", "10-3-2024 10:00:00", "10-4-2024 09:10:00", "10-5-2024 08:02:00", "10-6-2024 00:00:00", "10-7-2024 00:32:00", "10-8-2024 00:50:00", "10-9-2024 21:50:00", "10-10-2024 23:59:00"],
            "date_missing": ["2024-10-1", "", "2024-10-3", "2024-10-4", "NA", "2024-10-6", "2024-10-7", " ", "2024-10-9", "NA-2"],
        },
    )

def test_init_success(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input)

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == test_input.expected_str_val

    if test_input.test_case in ["date", "missing_code"]:
        assert np.isnan(rc_num.num_val)
    else:
        assert rc_num.num_val == test_input.expected_num_val


def test_init_invalid_param_type() -> None:
    with pytest.raises(TypeError):
        RedcapNumber(123)  # type: ignore[reportArgumentType]


def test_init_object_equality(test_input: TestInput) -> None:
    rc_num_1 = RedcapNumber(test_input.test_input)
    rc_num_2 = RedcapNumber(test_input.test_input)
    rc_num_3 = RedcapNumber("other_value")

    assert rc_num_1 is rc_num_2
    assert rc_num_1 is not rc_num_3
    assert rc_num_2 is not rc_num_3


@pytest.mark.parametrize(
        "date_str",
        [
            "20-09-2024", "09-20-2024", "2024-09-20",
            "20-09-2024 00:00", "09-20-2024 00:00", "2024-09-20 00:00",
            "20-09-2024 00:00:00", "09-20-2024 00:00:00", "2024-09-20 00:00:00",  # NOQA: E501
            "20-09-2024 15:35:52",
         ],
 )
def test_init_alternate_date_format(date_str: str) -> None:
    rc_num = RedcapNumber(date_str)

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == date_str
    assert np.isnan(rc_num.num_val)


def test_init_invalid_date() -> None:
    rc_num = RedcapNumber("Jun 20, 2024")

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == "Jun 20, 2024"
    assert np.isnan(rc_num.num_val)


def test_init_negative_number() -> None:
    rc_num = RedcapNumber("-13")

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == "-13"
    assert rc_num.num_val == -13.0


def test_eq_true(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input)

    assert rc_num == test_input.expected_str_val


def test_eq_false(redcap_number: RedcapNumber) -> None:
    raise NotImplementedError


def test_lt_success() -> None:
    raise NotImplementedError


def test_lt_invalid_comparison_type() -> None:
    raise NotImplementedError


def test_le_success() -> None:
    raise NotImplementedError


def test_le_invalid_comparison_type() -> None:
    raise NotImplementedError


def test_gt_success() -> None:
    raise NotImplementedError


def test_gt_invalid_comparison_type() -> None:
    raise NotImplementedError


def test_ge_success() -> None:
    raise NotImplementedError


def test_ge_invalid_comparison_type() -> None:
    raise NotImplementedError


def test_add_success() -> None:
    raise NotImplementedError


def test_add_invalid_type() -> None:
    raise NotImplementedError


def test_sub_success() -> None:
    raise NotImplementedError


def test_sub_invalid_type() -> None:
    raise NotImplementedError


def test_mul_success() -> None:
    raise NotImplementedError


def test_mul_invalid_type() -> None:
    raise NotImplementedError


def test_truediv_success() -> None:
    raise NotImplementedError


def test_truediv_invalid_type() -> None:
    raise NotImplementedError


