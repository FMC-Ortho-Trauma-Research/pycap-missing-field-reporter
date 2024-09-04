import re
from typing import ClassVar

import numpy as np

from pycap_mfr.data.config.config import MISSING_STRING_LIT


class RedcapNumber:
    _instances: ClassVar[dict[str, "RedcapNumber"]] = {}
    MISSING_STRING_PATT = re.compile(MISSING_STRING_LIT)

    def __init__(self, value: str) -> None:
        if not hasattr(self, "_initialized"):
            val_type, str_val, num_val = self._check_value(value)
            self._val_type = val_type
            self._str_val = str_val
            self._num_val = num_val
            self._initialized = True

    def __new__(cls, value: str) -> "RedcapNumber":
        if value not in cls._instances:
            redcap_number = super().__new__(cls)
            cls._instances[value] = redcap_number
        return cls._instances[value]

    @classmethod
    def get_instance(cls, value: str) -> "RedcapNumber":
        if value not in cls._instances:
            return cls(value)
        return cls._instances[value]

    @property
    def str_value(self) -> str:
        return self._str_val

    @property
    def num_value(self) -> float:
        return self._num_val

    def __hash__(self) -> int:
        hash_val = 0
        match self._val_type:
            case "number":
                hash_val = hash(self._num_val)
            case "text":
                hash_val = hash(self._str_val)
            case "missing":
                hash_val = hash(self._str_val)
            case _:
                err_str = f"Unhashable data: {self._str_val, self._num_val}"
                raise TypeError(err_str)
        return hash_val

    def __str__(self) -> str:
        return self._str_val

    def __float__(self) -> float:
        return self._num_val

    def __repr__(self) -> str:
        return f"RedcapNumber(str={self._str_val}, value={self._num_val})"

    def __eq__(self, other: object) -> bool:
        match other:
            case RedcapNumber():
                return self._num_val == other.num_value
            case str():
                return self._str_val == other
            case int() | float():
                return self._num_val == other
            case _:
                return False

    def __lt__(self, other: "RedcapNumber | float" ) -> bool:
        return self._num_val < other

    def __le__(self, other: float) -> bool:
        return self._num_val <= other

    def __gt__(self, other: float) -> bool:
        return self._num_val > other

    def __ge__(self, other: float) -> bool:
        return self._num_val >= other

    def __add__(self, other: float) -> float:
        return self._num_val + other

    def __sub__(self, other: float) -> float:
        return self._num_val - other

    def __mul__(self, other: float) -> float:
        return self._num_val * other

    def __truediv__(self, other: float) -> float:
        return self._num_val / other

    def __floordiv__(self, other: float) -> float:
        return self._num_val // other

    def _check_value(self, value: str) -> tuple[str, str, float]:
        if not isinstance(value, str):
            err_str = f"Expected a str, but got type: {type(value)}!"
            raise TypeError(err_str)
        str_val = value

        try:
            num_value = float(value)
            val_type = "number"
        except ValueError:
            num_value = np.nan
            val_type = "text"

        if re.fullmatch(self.MISSING_STRING_PATT, value):
            str_val = ""
            val_type = "missing"

        return val_type, str_val, num_value
