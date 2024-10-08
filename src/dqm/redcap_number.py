from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import ClassVar, TypeAlias
from weakref import WeakValueDictionary

import numpy as np
from numpy import typing as npt
from pandas.api.extensions import ExtensionArray, register_extension_dtype
from pandas.core.dtypes.dtypes import PandasExtensionDtype

from dqm.config import ALLOWED_DATE_FORMATS, MISSING_DATA_CODES

TakeIndexer: TypeAlias = (
    Sequence[int] | Sequence[np.integer] | npt.NDArray[np.integer]
)


class RedcapNumber:
    _instances: ClassVar[WeakValueDictionary[str, "RedcapNumber"]] = (
        WeakValueDictionary()
    )
    _str_val: str
    _num_val: float
    _dtype: str

    def __new__(cls, input_str: str) -> "RedcapNumber":
        if not isinstance(input_str, str):
            err_str = f"Unexpected type for param: input_str. Expected str type, but got {type(input_str)}!"  # NOQA: E501
            raise TypeError(err_str)

        self = cls._instances.get(input_str)

        if self is None:
            self = cls._instances[input_str] = object.__new__(RedcapNumber)
            self._str_val, self._num_val, self._dtype = self._identify_input(
                input_str,
            )

        return self

    @property
    def str_val(self) -> str:
        return self._str_val

    @property
    def num_val(self) -> float:
        return self._num_val

    @property
    def dtype(self) -> str:
        return self._dtype

    def __repr__(self) -> str:
        return f"RedcapNumber(str={self._str_val}, num={self._num_val}, dtype={self._dtype})"  # NOQA: E501

    def __str__(self) -> str:
        return self._str_val

    def __float__(self) -> float:
        return self._num_val

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RedcapNumber | str | float | int):
            return NotImplemented

        match self._dtype:
            case "empty":
                return self._is_empty_eq(other)
            case "number":
                return self._is_eq(other)
            case "code" | "date" | "text":
                return self._is_eq(other)
            case _:
                return NotImplemented

    def _is_empty_eq(self, other: "RedcapNumber | str | float") -> bool:
        match other:
            case RedcapNumber():
                return any(
                    (
                        getattr(other, "dtype", None) == "empty",
                        getattr(other, "str_val", None) == "",
                        getattr(other, "num_val", None) == 0.0,
                    ),
                )
            case str():
                return other in ("", "0", "0.0")
            case float() | int():
                return other == 0.0
            case _:
                return NotImplemented

    def _is_eq(self, other: "RedcapNumber | str | float") -> bool:
        match other:
            case RedcapNumber():
                if self._dtype == "number":
                    return self._num_val == getattr(other, "num_val", None)
                if self._dtype in ("code", "date", "text"):
                    return self._str_val == getattr(other, "str_val", None)
                return NotImplemented
            case str():
                return self._str_val == other
            case float() | int():
                return self._num_val == other
            case _:
                return NotImplemented

    # TODO: Fix these methods to handle dates and text better.
    #       Should perform string comparisons for dates or text values.
    #       Comparison is based on the dtype of the RedcapNumber object.
    def __lt__(self, other: "RedcapNumber | float") -> bool:
        val = self._validate_number(other)
        return self._num_val < val

    def __le__(self, other: "RedcapNumber | float") -> bool:
        val = self._validate_number(other)
        return self._num_val <= val

    def __gt__(self, other: "RedcapNumber | float") -> bool:
        val = self._validate_number(other)
        return self._num_val > val

    def __ge__(self, other: "RedcapNumber | float") -> bool:
        val = self._validate_number(other)
        return self._num_val >= val

    def __add__(self, other: "RedcapNumber | float") -> float:
        val = self._validate_number(other)
        return self._num_val + val

    def __sub__(self, other: "RedcapNumber | float") -> float:
        val = self._validate_number(other)
        return self._num_val - val

    def __mul__(self, other: "RedcapNumber | float") -> float:
        val = self._validate_number(other)
        return self._num_val * val

    def __truediv__(self, other: "RedcapNumber | float") -> float:
        val = self._validate_number(other)
        return self._num_val / val

    def _identify_input(self, input_str: str) -> tuple[str, float, str]:
        if input_str == "":
            return ("", 0.0, "empty")

        if MISSING_DATA_CODES and input_str in MISSING_DATA_CODES:
            return (input_str, np.nan, "code")

        try:
            num_val = float(input_str)
        except (OverflowError, TypeError, ValueError):
            pass
        else:
            return (input_str, num_val, "number")

        for dt_fmt in ALLOWED_DATE_FORMATS:
            try:
                datetime.strptime(input_str, dt_fmt)  # NOQA: DTZ007
            except ValueError:
                pass
            else:
                return (input_str, np.nan, "date")

        return (input_str, np.nan, "text")

    def _validate_number(self, other: "RedcapNumber | float | str") -> float:
        try:
            num_val = float(other)
        except (OverflowError, TypeError, ValueError) as e:
            err_str = f"Invalid comparison, expected numeric type but got {type(other)}"  # NOQA: E501
            raise TypeError(err_str) from e
        else:
            return num_val


@register_extension_dtype
class RedcapNumberDtype(PandasExtensionDtype):
    name = "rc_num"
    type = RedcapNumber

    def __str__(self) -> str:
        return self.name

    @classmethod
    def construct_array_type(cls) -> "type[RedcapNumberArray]":
        return RedcapNumberArray


class RedcapNumberArray(ExtensionArray):
    def __init__(
        self,
        num_values: Iterable[float],
        str_values: Iterable[str],
        copy: bool = False,  # NOQA: FBT001, FBT002
    ) -> None:
        self.num_values = np.array(num_values, dtype=np.float64, copy=copy)
        self.str_values = np.array(str_values, dtype=np.str_, copy=copy)

    @classmethod
    def _from_sequence(
        cls,
        scalars: Iterable[str],
        *,
        dtype: str | None = None,  # NOQA: ARG003
        copy: bool = False,
    ) -> "RedcapNumberArray":
        num_values, str_values = zip(
            *[
                (RedcapNumber(val).num_val, RedcapNumber(val).str_val)
                for val in scalars
            ],
            strict=True,
        )
        return RedcapNumberArray(num_values, str_values, copy=copy)

    def __getitem__(
        self,
        item: int | slice,
    ) -> "RedcapNumber | RedcapNumberArray":
        match item:
            case int():
                return RedcapNumber(self.str_values[item])
            case slice():
                return RedcapNumberArray(
                    self.num_values[item],
                    self.str_values[item],
                )
            case _:
                err_str = f"Invalid index type, expected int or slice but got {type(item)}"  # NOQA: E501
                raise TypeError(err_str)

    def __len__(self) -> int:
        return self.num_values.size

    def __eq__(self, other: str) -> np.ndarray:
        try:
            other = str(other)
        except Exception as e:
            err_str = f"Invalid comparison, expected str but got {type(other)}"
            raise TypeError(err_str) from e

        return self.str_values == other

    @property
    def dtype(self) -> RedcapNumberDtype:
        return RedcapNumberDtype()

    @property
    def nbytes(self) -> int:
        return self.num_values.nbytes + self.str_values.nbytes

    def isna(self) -> np.ndarray:
        return np.isnan(self.num_values)

    def copy(self) -> "RedcapNumberArray":
        return RedcapNumberArray(
            np.copy(self.num_values),
            np.copy(self.str_values),
        )

    # The type hint for take() in base.pyi is different to the documentation
    def take(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        indices: TakeIndexer,
        *,
        allow_fill: bool = False,
        fill_value=None,
    ) -> "RedcapNumberArray":
        from pandas.core.algorithms import take

        if allow_fill and fill_value is None:
            fill_value = self.dtype.na_value

        num_values = take(
            self.num_values,
            indices,
            allow_fill=allow_fill,
            fill_value=fill_value,
        )
        str_values = take(
            self.str_values,
            indices,
            allow_fill=allow_fill,
            fill_value=fill_value,
        )

        return RedcapNumberArray(num_values, str_values)

    @classmethod
    def _concat_same_type(
        cls,
        to_concat: Iterable["RedcapNumberArray"],
    ) -> "RedcapNumberArray":
        return RedcapNumberArray(
            np.concatenate([arr.num_values for arr in to_concat]),
            np.concatenate([arr.str_values for arr in to_concat]),
        )

    def __lt__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values < self._validate_number(other)

    def __le__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values <= self._validate_number(other)

    def __gt__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values > self._validate_number(other)

    def __ge__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values >= self._validate_number(other)

    def __add__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values + self._validate_number(other)

    def __sub__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values - self._validate_number(other)

    def __mul__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values * self._validate_number(other)

    def __truediv__(self, other: str | float | RedcapNumber) -> np.ndarray:
        return self.num_values / self._validate_number(other)

    def _validate_number(self, other: str | float | RedcapNumber) -> float:
        err_str = (
            f"Invalid comparison, expected numeric type but got {type(other)}"
        )
        match other:
            case RedcapNumber():
                return other.num_val
            case float() | int():
                return other
            case str():
                try:
                    return RedcapNumber(other).num_val
                except Exception as e:
                    raise TypeError(err_str) from e
            case _:
                raise TypeError(err_str)

    def _calculate_str_values(self, num_values: np.ndarray) -> np.ndarray:
        raise NotImplementedError
