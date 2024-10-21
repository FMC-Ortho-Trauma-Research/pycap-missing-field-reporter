from typing import NamedTuple

import numpy as np
import pandas as pd
import pytest
from dateutil.parser import parse
from pytest_mock import MockerFixture

from dqm.redcap_number import RedcapNumber, RedcapNumberArray


class TestInput(NamedTuple):
    test_name: str
    test_input_str: str
    expected_str_val: str
    expected_num_val: float

missing = TestInput("missing", "", "", 0.0)
missing_code = TestInput("missing_code", "NA-2", "NA-2", np.nan)
date = TestInput("date", "2024-09-20", "2024-09-20", np.nan)
text = TestInput("text", "text", "text", np.nan)
category = TestInput("category", "2", "2", 2.0)
numeric = TestInput("numeric", "23.6", "23.6", 23.6)


@pytest.fixture(
    params=[missing, missing_code, date, text, category, numeric],
    ids=["missing", "missing_code", "date", "text", "category", "numeric"],
)
def test_input(request: pytest.FixtureRequest) -> TestInput:
    return request.param


def test_init_success(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == test_input.expected_str_val

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
    else:
        assert rc_num.num_val == test_input.expected_num_val


def test_init_invalid_param_type() -> None:
    with pytest.raises(TypeError):
        RedcapNumber(123)  # type: ignore[reportArgumentType]


def test_init_object_equality(test_input: TestInput) -> None:
    rc_num_1 = RedcapNumber(test_input.test_input_str)
    rc_num_2 = RedcapNumber(test_input.test_input_str)
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


def test_init_negative_number() -> None:
    rc_num = RedcapNumber("-13")

    assert isinstance(rc_num, RedcapNumber)
    assert isinstance(rc_num.str_val, str)
    assert isinstance(rc_num.num_val, float)

    assert rc_num.str_val == "-13"
    assert rc_num.num_val == -13.0


def test_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert isinstance(str(rc_num), str)
    assert str(rc_num) == test_input.expected_str_val


def test_float(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert isinstance(float(rc_num), float)
    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(float(rc_num))
    else:
        assert float(rc_num) == test_input.expected_num_val


def test_eq(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert rc_num == test_input.expected_str_val

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
    else:
        assert rc_num == test_input.expected_num_val


def test_eq_invalid_type() -> None:
    rcn = RedcapNumber("13")

    assert rcn == 13
    assert rcn == 13.0
    assert rcn == "13"

    assert rcn != (13,)
    assert rcn != [13]
    assert not rcn == {"value": 13}  # NOQA: SIM201


def test_eq_missing() -> None:
    rcn = RedcapNumber("")
    rcn_empty = RedcapNumber("")
    rcn_0 = RedcapNumber("0")
    rcn_nan = RedcapNumber("nan")

    assert rcn.dtype == "MISSING"
    assert rcn == ""
    assert rcn == 0
    assert rcn == 0.0
    assert rcn != "0"
    assert rcn == rcn_empty
    assert rcn == rcn_0
    assert rcn != "other_text"
    assert rcn != rcn_nan


def test_eq_numeric() -> None:
    rc_num_13 = RedcapNumber("13")
    rc_num_13_0 = RedcapNumber("13.0")

    assert rc_num_13 == 13
    assert rc_num_13 == 13.0
    assert rc_num_13 == "13"
    assert rc_num_13 != "13.0"
    assert rc_num_13_0 == 13
    assert rc_num_13_0 == 13.0
    assert rc_num_13_0 != "13"
    assert rc_num_13_0 == "13.0"
    assert rc_num_13 != rc_num_13_0
    assert float(rc_num_13) == float(rc_num_13_0)


def test_lt_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num != 0
        assert not rc_num < 0
        assert not rc_num > 0
    else:
        assert rc_num < test_input.expected_num_val + 1


def test_lt_str() -> None:
    rc_num_4 = RedcapNumber("4")
    rc_num_13 = RedcapNumber("13")

    assert rc_num_4 < 5
    assert rc_num_4 < 5.0
    assert rc_num_4 < "5"
    assert rc_num_4 < "5.0"
    assert rc_num_13 < 14
    assert rc_num_13 < 14.0
    assert rc_num_13 < "14"
    assert rc_num_13 < "14.0"

    assert not rc_num_13 < 4
    assert rc_num_13 < "4"
    assert rc_num_13 < rc_num_4


def test_le_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert not rc_num <= 0
        assert not rc_num > 0
    else:
        assert rc_num <= test_input.expected_num_val
        assert rc_num <= test_input.expected_num_val + 1
        assert not rc_num <= test_input.expected_num_val - 1


def test_le_str() -> None:
    rc_num_4 = RedcapNumber("4")
    rc_num_13 = RedcapNumber("13")

    assert rc_num_4 <= 4
    assert rc_num_4 <= 4.0
    assert rc_num_4 <= "4"
    assert rc_num_4 <= "4.0"
    assert rc_num_13 <= 13
    assert rc_num_13 <= 13.0
    assert rc_num_13 <= "13"
    assert rc_num_13 <= "13.0"

    assert not rc_num_13 <= 4
    assert rc_num_13 <= "4"
    assert rc_num_13 <= rc_num_4


def test_gt_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num != 0
        assert not rc_num < 0
        assert not rc_num > 0
    else:
        assert rc_num > test_input.expected_num_val - 1


def test_gt_str() -> None:
    rc_num_4 = RedcapNumber("4")
    rc_num_13 = RedcapNumber("13")

    assert rc_num_4 > 3
    assert rc_num_4 > 3.0
    assert rc_num_4 > "3"
    assert rc_num_4 > "3.0"
    assert rc_num_13 > 12
    assert rc_num_13 > 12.0
    assert rc_num_13 > "12"
    assert rc_num_13 > "12.0"

    assert not rc_num_4 > 13
    assert rc_num_4 > "13"
    assert rc_num_4 > rc_num_13


def test_ge_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert not rc_num <= 0
        assert not rc_num > 0
    else:
        assert rc_num >= test_input.expected_num_val
        assert rc_num >= test_input.expected_num_val - 1
        assert not rc_num >= test_input.expected_num_val + 1


def test_ge_str() -> None:
    rc_num_4 = RedcapNumber("4")
    rc_num_13 = RedcapNumber("13")

    assert rc_num_4 >= 4
    assert rc_num_4 >= 4.0
    assert rc_num_4 >= "4"
    assert not rc_num_4 >= "4.0"
    assert rc_num_13 >= 13
    assert rc_num_13 >= 13.0
    assert rc_num_13 >= "13"
    assert not rc_num_13 >= "13.0"

    assert not rc_num_4 >= 13
    assert rc_num_4 >= "13"
    assert rc_num_4 >= rc_num_13


def test_add_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num + 1 != 1
        assert rc_num + 1 != 0
    else:
        assert isinstance(rc_num + 1, float)
        assert rc_num + 1 == test_input.expected_num_val + 1


def test_add_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)
    str_values = ("1", "1.0", "01", "-1", "-1.0", "-01")
    numeric_values = (1, 1.0, 1, -1, -1.0, -1)

    for str_val, num_val in zip(str_values, numeric_values, strict=True):
        if test_input.test_name in ["date", "text", "missing_code"]:
            assert np.isnan(rc_num + str_val)
        else:
            assert isinstance(rc_num + str_val, float)
            assert rc_num + str_val == test_input.expected_num_val + num_val


def test_add_invalid_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert np.isnan(rc_num + "invalid")


def test_sub_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num - 1 != 1
        assert rc_num - 1 != 0
    else:
        assert isinstance(rc_num - 1, float)
        assert rc_num - 1 == test_input.expected_num_val - 1


def test_sub_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)
    str_values = ("1", "1.0", "01", "-1", "-1.0", "-01")
    numeric_values = (1, 1.0, 1, -1, -1.0, -1)

    for str_val, num_val in zip(str_values, numeric_values, strict=True):
        if test_input.test_name in ["date", "text", "missing_code"]:
            assert np.isnan(rc_num - str_val)
        else:
            assert isinstance(rc_num - str_val, float)
            assert rc_num - str_val == test_input.expected_num_val - num_val


def test_sub_invalid_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert np.isnan(rc_num - "invalid")


def test_mul_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num * 2 != 2
        assert rc_num * 2 != 0
    else:
        assert isinstance(rc_num * 2, float)
        assert rc_num * 2 == test_input.expected_num_val * 2


def test_mul_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)
    str_values = ("2", "2.0", "02", "-2", "-2.0", "-02")
    numeric_values = (2, 2.0, 2, -2, -2.0, -2)

    for str_val, num_val in zip(str_values, numeric_values, strict=True):
        if test_input.test_name in ["date", "text", "missing_code"]:
            assert np.isnan(rc_num * str_val)
        else:
            assert isinstance(rc_num * str_val, float)
            assert rc_num * str_val == test_input.expected_num_val * num_val


def test_mul_invalid_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert np.isnan(rc_num * "invalid")


def test_truediv_numeric(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    if test_input.test_name in ["date", "text", "missing_code"]:
        assert np.isnan(rc_num.num_val)
        assert rc_num / 2 != 2
        assert rc_num / 2 != 0
    else:
        assert isinstance(rc_num / 2, float)
        assert rc_num / 2 == test_input.expected_num_val / 2


def test_truediv_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)
    str_values = ("2", "2.0", "02", "-2", "-2.0", "-02")
    numeric_values = (2, 2.0, 2, -2, -2.0, -2)

    for str_val, num_val in zip(str_values, numeric_values, strict=True):
        if test_input.test_name in ["date", "text", "missing_code"]:
            assert np.isnan(rc_num / str_val)
        else:
            assert isinstance(rc_num / str_val, float)
            assert rc_num / str_val == test_input.expected_num_val / num_val


def test_truediv_invalid_str(test_input: TestInput) -> None:
    rc_num = RedcapNumber(test_input.test_input_str)

    assert np.isnan(rc_num / "invalid")


def test_truediv_zero() -> None:
    rc_num = RedcapNumber("13")

    result = rc_num / 0

    assert np.isnan(result)


def test_arithmetic_unsupported_type() -> None:
    rc_num = RedcapNumber("13")

    with pytest.raises(NotImplementedError):
        _ = rc_num * [13]


# TODO: Figure out if this is a real Pylance error
def test_init_pandas_extension_dtype_success() -> None:
    response_values = ["", "NA-2", "2024-09-20", "text", "2", "23.6"]
    base_series = pd.Series(response_values, dtype="object")

    rcn_arr = pd.array(response_values, dtype="rc_num")
    rcn_series = pd.Series(response_values, dtype="rc_num")
    rcn_series_from_base = base_series.astype(dtype="rc_num")

    assert isinstance(rcn_arr, RedcapNumberArray)
    assert len(rcn_arr) == len(response_values)

    assert isinstance(rcn_series, pd.Series)
    assert len(rcn_series) == len(response_values)

    assert isinstance(rcn_series_from_base, pd.Series)
    assert len(rcn_series_from_base) == len(response_values)
