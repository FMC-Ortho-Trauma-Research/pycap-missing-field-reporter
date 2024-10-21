from collections.abc import Callable, Iterable, Sequence
from enum import StrEnum
from typing import ClassVar, TypeAlias
from weakref import WeakValueDictionary

import numpy as np
import pandas as pd
from numpy import typing as npt
from pandas.api.extensions import ExtensionArray, register_extension_dtype
from pandas.core.dtypes.dtypes import PandasExtensionDtype


class RCNDtype(StrEnum):
    """
    String enumeration for the expected response value types in REDCap.
    Kinda pointless, but makes the expected categories more explicit.

    Members
    -------
    MISSING : str
        Represents data that is missing (i.e an empty field). It is
        represented by an empty string `""` in REDCap, and has a value
        of 0.0 for the purposes of arithmetic operations.
    NUMBER : str
        Represents a string-input that represents a valid numeric value.
        This includes free-text numbers and multiple-choice response
        codes in REDCap.
    TEXT : str
        Represents `true` text values, This includes missing data codes,
        dates, and free-text responses in REDCap.
        REDCap calculation errors, which seem to have the str value `""`
        but have a numeric value of np.nan, are also considered as TEXT
        because I'm to lazy to figure out how to differentiate them from
        missing values, since they will both look like `""` from REDCap.
    """

    MISSING = "MISSING"
    NUMBER = "NUMBER"
    TEXT = "TEXT"


class RedcapNumber:
    """
    A class used to mimic REDCap's internal handling of response values.

    REDCap stores all response values as strings internally, but allows
    these values to be considered in comparison or arithmetic operations
    as either strings or numbers depending on the context.
    This class allows for comparison and arithmetic operations between
    response values and strings OR numbers without raising TypeErrors,
    and trying to mimic the behaviour of REDCap as closely as possible.

    Attributes
    ----------
    _instances : WeakValueDictionary[str, RedcapNumber]
        A WeakValueDictionary is used to implement a singleton pattern
        in REDCapNumber so that instances can be garbage collected when
        no longer in use to free memory.
    _str_val : str
        A string representation of the response value.
    _num_val : float
        A numeric representation of the response value.
    _dtype : RCNDtype
        The parsed data type of the response value corresponding to one
        of the members of the RCNDtype enumeration.

    Methods
    -------
    str_val() -> str
        Returns the string representation of the response value.
    num_val() -> float
        Returns the numeric representation of the response value.
    dtype() -> RCNDtype
        Returns the parsed data type of the response value.
    __new__(cls, input_str: str) -> RedcapNumber
        Returns an existing REDCapNumber object, or creates a new one if
        the input_str is not already an existing instance.

    """

    _instances: ClassVar[WeakValueDictionary[str, "RedcapNumber"]] = (
        WeakValueDictionary()
    )
    _str_val: str
    _num_val: float
    _dtype: RCNDtype

    def __new__(cls, input_str: str) -> "RedcapNumber":
        """
        Returns a REDCapNumber object for the given input_str.

        This method implements a singleton pattern to save memory on
        repeated creation of REDCapNumber objects for the same input.
        If the input corresponds to an existing REDCapNumber in the
        _instances dictionary, the existing object is returned, else a
        new REDCapNumber object is created and added to the dictionary.

        Parameters
        ----------
        input_str : str
            The response value to be represented as a REDCapNumber obj.

        Raises
        ------
        TypeError
            If the input_str is not of type str.
            We only expect string values as input for consistency with
            REDCap's internal handling of response values.
            If the input is not a string, there's a good chance
            something messed up, or will soon.

        """
        if isinstance(input_str, RedcapNumber):
            return input_str

        if not isinstance(input_str, str):
            err_str = f"RedcapNumber() expected param: `input_str` to be of type str, but got type: {type(input_str)}!"  # NOQA: E501
            raise TypeError(err_str)

        self = cls._instances.get(input_str)

        if self is None:
            self = cls._instances[input_str] = object.__new__(RedcapNumber)
            self._str_val, self._num_val, self._dtype = self._identify_input(
                input_str,
            )

        return self

    # TODO: Check if REDCap calculation errors are handled correctly
    def _identify_input(self, input_str: str) -> tuple[str, float, RCNDtype]:
        """
        Parses the input string and returns a tuple of its string and
        numeric representations, and the category of the response value.

        Parameters
        ----------
        input_str : str
            The response value to be parsed.

        """
        # Missing data
        if not input_str:
            return ("", 0.0, RCNDtype.MISSING)
        # Numeric data
        if self._is_numeric_str(input_str):
            return (input_str, float(input_str), RCNDtype.NUMBER)
        # Otherwise, treat as text data
        return (input_str, np.nan, RCNDtype.TEXT)

    @property
    def str_val(self) -> str:
        """Returns the string representation of the response value."""
        return self._str_val

    @property
    def num_val(self) -> float:
        """Returns the numeric representation of the response value."""
        return self._num_val

    @property
    def dtype(self) -> RCNDtype:
        """Returns the category of the response value."""
        return self._dtype

    def __repr__(self) -> str:
        """Returns details of the REDCapNumber object."""
        return f"<class 'RedcapNumber': str_val='{self._str_val}', num_val={self._num_val}, dtype={self._dtype}>"  # NOQA: E501

    def __str__(self) -> str:
        """Returns the string representation of the response value."""
        return self._str_val

    def __float__(self) -> float:
        """Returns the numeric representation of the response value."""
        return self._num_val

    def __hash__(self) -> int:
        """
        Returns the hash of response value represented by this
        RedcapNumber instance.

        This method returns the hash of the string representation of the
        response value since the string representation is unique for
        every instance of the RedcapNumber class.

        Returns
        -------
        int
            The hash of the string representation of the response value.

        """
        return hash(self._str_val)

    def __eq__(self, other: object) -> bool:
        """
        Check if the other object is equal to the response value
        represented by this RedcapNumber instance.

        This method returns a boolean value indicating whether the other
        object is equal to the response value represented by the current
        instance of the REDCapNumber class. The equality of two response
        values in REDCap is dependent on the category of the responses.

        Parameters
        ----------
        other : object
            The object to be compared to the response value. Supported
            types for comparison are str, float, int, and RedcapNumber
            (i.e. a response value being compared to another response).

        Returns
        -------
        bool
            True if the other object is equal to the response value,
            False otherwise. Returns NotImplemented if the other object
            is unsupported for comparison.

        """
        if not isinstance(other, RedcapNumber | str | float | int):
            return NotImplemented

        match self._dtype:
            case RCNDtype.MISSING:
                return self._is_other_missing(other)
            case RCNDtype.TEXT:
                return self._is_other_eq_txt(other)
            case RCNDtype.NUMBER:
                return self._is_other_eq_num(other)
            case _:
                return NotImplemented

    def _is_other_missing(self, other: "RedcapNumber | str | float") -> bool:
        """
        Check if the other object represents a missing value.

        This method determines if the other object is considered equal
        to a missing value. A missing value can be an empty string,
        a response with a numeric value of 0, or another RedcapNumber
        instance with a dtype of MISSING.
        Missing response values have a numeric value of 0, but REDCap
        does not coerce 0-like strings to their numeric values. e.g.
            - RedcapNumber("") == 0     => True
            - RedcapNumber("") == 0.0   => True
            - RedcapNumber("") == "0"   => False

        Parameters
        ----------
        other : RedcapNumber | str | float
            The object to compare against. Due to the guard clause in
            the __eq__() method, this should only be a RedcapNumber,
            str, float, or int.

        Returns
        -------
        bool
            True if the other object represents a missing value, False
            otherwise. Returns NotImplemented if the comparison is
            performed with unsupported types, however, this should never
            happen due to the guard clause in the __eq__() method.

        """
        match other:
            case RedcapNumber():
                return any(
                    (
                        getattr(other, "dtype", None) == RCNDtype.MISSING,
                        getattr(other, "str_val", None) == "",
                        getattr(other, "num_val", None) == 0.0,
                    ),
                )
            case str():
                return other == ""
            case float() | int():
                return other == 0.0
            case _:
                return NotImplemented

    def _is_other_eq_txt(self, other: "RedcapNumber | str | float") -> bool:
        """
        Check if the other object is equal to the string value of the
        response represented by the current RedcapNumber instance.

        This method should only be called by __eq__() when the current
        instance of RedcapNumber was parsed to represent a TEXT value by
        the _identify_input() method. Since _identify_input() should
        have classidied any number-like str as a NUMBER, it follows that
        if we reach this point and the other object is a valid numeric
        value, it should never be equal to the response value
        represented by the current RedcapNumber instance. Thus, we can
        safely return False for that comparison.

        Parameters
        ----------
        other : RedcapNumber | str | float
            The object to compare against. Due to the guard clause in
            the __eq__() method, this should only be a RedcapNumber,
            str, float, or int.

        Returns
        -------
        bool
            True if the other object is equal to the text value, False
            otherwise. Returns NotImplemented if the comparison is
            performed with unsupported types, however, this should never
            happen due to the guard clause in the __eq__() method.

        """
        match other:
            case RedcapNumber():
                return self._str_val == getattr(other, "str_val", None)
            case str():
                return self._str_val == other
            # Numeric value should never be equal to `pure` text
            case float() | int():
                return False
            case _:
                return NotImplemented

    def _is_other_eq_num(self, other: "RedcapNumber | str | float") -> bool:
        """
        Check if the other object is equal to the numeric value of the
        response represented by the current RedcapNumber instance.

        REDCap does NOT coerce number-like strings to their numeric
        values in the equality comparison, so:
            - RedcapNumber("1")   == 1                      => True
            - RedcapNumber("1")   == "1"                    => True
            - RedcapNumber("1")   == 1.0                    => True
            - RedcapNumber("1")   == "1.0"                  => False
            - RedcapNumber("1.0") == 1                      => True
            - RedcapNumber("1.0") == "1.0"                  => True
            - RedcapNumber("1.0") == "1"                    => False
            - RedcapNumber("1.0") == RedcapNumber("1.0")    => True
            - RedcapNumber("1.0") == RedcapNumber("1")      => False

        Parameters
        ----------
        other : RedcapNumber | str | float
            The object to compare against. Due to the guard clause in
            the __eq__() method, this should only be a RedcapNumber,
            str, float, or int.

        Returns
        -------
        bool
            True if the other object represents a missing value, False
            otherwise. Returns NotImplemented if the comparison is
            performed with unsupported types, however, this should never
            happen due to the guard clause in the __eq__() method.

        """
        match other:
            case RedcapNumber():
                return self._str_val == getattr(other, "str_val", None)
            case str():
                return self._str_val == other
            case float() | int():
                return self._num_val == other
            case _:
                return NotImplemented

    def __lt__(self, other: object) -> bool:
        """
        Check if the response value represented by the current instance
        of RedcapNumber is less than another object.

        This method compares the response value with another object to
        check if it is less than the other object. REDCap defaults to
        lexicographical ordering when comparing response values to str
        values or to other response values. This is consistent with
        Python's built-in string comparison methods. e.g.
            - RedcapNumber("12") < "13"                 => True
            - RedcapNumber("2")  <  13                  => True
            - RedcapNumber("2")  < "13"                 => False
            - RedcapNumber("2")  <  RedcapNumber("13")  => False

        Parameters
        ----------
        other : object
            The object to compare against.

        Returns
        -------
        bool
            True if the response value is less than the other object,
            False otherwise. Returns NotImplemented (from the
            _compare_values() method) if the comparison isn't supported.

        """
        return self._compare_values(other, lambda self, other: self < other)

    def __le__(self, other: object) -> bool:
        """
        Check if the response value represented by the current instance
        of RedcapNumber is less than or equal to another object.

        This method compares the response value with another object to
        check if it is less than or equal to the other object. REDCap
        defaults to lexicographical ordering when comparing response
        values to str values or to other response values. This is
        consistent with Python's built-in str comparison methods. e.g.
            - RedcapNumber("13") <= "13"                => True
            - RedcapNumber("12") <=  13                 => True
            - RedcapNumber("2")  <= "13"                => False
            - RedcapNumber("2")  <=  RedcapNumber("13") => False

        Parameters
        ----------
        other : object
            The object to compare against.

        Returns
        -------
        bool
            True if the response value is less or equal to the other
            object, False otherwise. Returns NotImplemented (from the
            _compare_values() method) if the comparison isn't supported.

        """
        return self._compare_values(other, lambda self, other: self <= other)

    def __gt__(self, other: object) -> bool:
        """
        Check if the response value represented by the current instance
        of RedcapNumber is greater than another object.

        This method compares the response value with another object to
        check if it is greater than the other object. REDCap defaults to
        lexicographical ordering when comparing response values to str
        values or to other response values. This is consistent with
        Python's built-in string comparison methods. e.g.
            - RedcapNumber("13") > "12"                 => True
            - RedcapNumber("13") >  2                   => True
            - RedcapNumber("13") > "13.0"               => False
            - RedcapNumber("13") > "2"                  => False
            - RedcapNumber("13") >  RedcapNumber("2")   => False

        Parameters
        ----------
        other : object
            The object to compare against.

        Returns
        -------
        bool
            True if the response value is greater than the other object,
            False otherwise. Returns NotImplemented (from the
            _compare_values() method) if the comparison isn't supported.

        """
        return self._compare_values(other, lambda self, other: self > other)

    def __ge__(self, other: object) -> bool:
        """
        Check if the response value represented by the current instance
        of RedcapNumber is greater than or equal to another object.

        This method compares the response value with another object to
        check if it is greater than or equal to the other object. REDCap
        defaults to lexicographical ordering when comparing response
        values to str values or to other response values. This is
        consistent with Python's built-in str comparison methods. e.g.
            - RedcapNumber("13") >=  12                 => True
            - RedcapNumber("13") >=  13                 => True
            - RedcapNumber("13") >= "13"                => True
            - RedcapNumber("13") >= "13.0"              => False
            - RedcapNumber("13") >= "2"                 => False
            - RedcapNumber("13") >=  RedcapNumber("2")  => False

        Parameters
        ----------
        other : object
            The object to compare against.

        Returns
        -------
        bool
            True if the response value is greater or equal to the other
            object, False otherwise. Returns NotImplemented (from the
            _compare_values() method) if the comparison isn't supported.

        """
        return self._compare_values(other, lambda self, other: self >= other)

    def _compare_values(self, other: object, comp_func: Callable) -> bool:
        """
        Check if the response value is <, <=, >, or >= the other object.

        This method contains the logic for comparing the response value
        represented by the current instance of RedcapNumber with another
        object. The comparison is done based on the category of the
        response value, and the type of the other object.

        REDCap uses lexicographical ordering when comparing response
        values to str-like values (values surrounded in "") or to other
        response values. e.g.
            - "4" > "13"    => True

        This is the same behaviour as that of Python's built-in string
        comparison methods. i.e. Comparing characters one by one, and if
        different, the character with the higher Unicode code point
        number is considered to be greater. If one string is a prefix of
        the other, the shorter string is guaranteed to be less than the
        longer string. This is significant since it means:
            - "13" < "13"       => False
            - "13" < "13.0"     => True

        RedcapNumber objects should only be created from response values
        so we treat comparisons with other RedcapNumber objects as
        comparisons between two strings even if the response values were
        parsed to be NUMBER. This is consistent with REDCap's logic.

        If other is numeric, REDCap will consider the response value as
        numeric as well. However, the numeric value of TEXT responses
        is np.nan, so comparisons between a TEXT response value and a
        numeric value will always return False. MISSING response values
        have a numeric value of 0.0, so no issues there.

        Parameters
        ----------
        other : object
            The object to compare against.
        comp_func : Callable
            The comparison function to be used for the comparison.
            e.g. self < other, self >= other, etc.

        Returns
        -------
        bool
            True if the response value is greater or equal to the other
            object, False otherwise. Returns NotImplemented if the
            comparison isn't supported, however this should never happen
            due to the _validate_other() method.

        """
        self._validate_other(other)

        match other:
            case RedcapNumber() | str():
                other_val = (
                    other.str_val if isinstance(other, RedcapNumber) else other
                )
                # Default to lexicographical ordering for TEXT values
                return comp_func(self._str_val, other_val)
            case float() | int():
                return (
                    # Comparison between a number and np.nan is always False
                    False
                    if self._dtype == RCNDtype.TEXT
                    # Otherwise compare using the numeric values
                    else comp_func(self._num_val, other)
                )
            case _:
                return NotImplemented

    def __add__(self, other: object) -> float:
        """
        Add the response value represented by the current instance of
        RedcapNumber to another object.

        This method performs addition between the response value and
        another object. Unlike the comparison operations, REDCap will
        coerce number-like strings to their numeric values when
        performing arithmetic operations. e.g.
            - RedcapNumber("12") +  1   => 13
            - RedcapNumber("12") + "1"  => 13

        REDCap does not perform str concatenation when adding TEXT-like
        values and instead returns np.nan. e.g.
            - RedcapNumber("text") +  1         => np.nan
            - RedcapNumber("text") + "1"        => np.nan
            - RedcapNumber("13")   + "text"     => np.nan

        Parameters
        ----------
        other : object
            The object to add to the response value.

        Returns
        -------
        float
            The result of the addition. Returns np.nan if the operation
            is done on objects of valid type (i.e. str, float, etc.),
            but the operation doesn't make sense. e.g. adding a TEXT
            response value to a numberic value.

        """
        return self._calculate_new_val(other, lambda self, other: self + other)

    def __sub__(self, other: object) -> float:
        """
        Subtract another object from the response value represented by
        the current instance of RedcapNumber.

        This method performs subtraction between the response value and
        another object. Unlike the comparison operations, REDCap will
        coerce number-like strings to their numeric values when
        performing arithmetic operations. i.e.
            - RedcapNumber("14") -  1   => 13
            - RedcapNumber("14") - "1"  => 13

        Parameters
        ----------
        other : object
            The object to subtract from the response value.

        Returns
        -------
        float
            The result of the subtraction. Returns np.nan if the
            operation is done on objects of valid type (i.e. str, float,
            etc.), but the operation doesn't make sense. e.g.
            subtracting a numeric value from a TEXT response value.

        """
        return self._calculate_new_val(other, lambda self, other: self - other)

    def __mul__(self, other: object) -> float:
        """
        Multiply the response value represented by the current instance
        of RedcapNumber with another object.

        This method performs multiplication between the response value
        and another object. Unlike the comparison operations, REDCap
        will coerce number-like strings to their numeric values when
        performing arithmetic operations. e.g.
            - RedcapNumber("13") *  1   => 13
            - RedcapNumber("13") * "1"  => 13

        REDCap does not perform str multiplication when multiplying
        TEXT-like values and numbers, and instead returns np.nan. e.g.
            - RedcapNumber("text") *  13        => np.nan
            - RedcapNumber("13")   * "text"     => np.nan

        Parameters
        ----------
        other : object
            The object to multiply with the response value.

        Returns
        -------
        float
            The result of the multiplication. Returns np.nan if the
            operation is done on objects of valid type (i.e. str, float,
            etc.), but the operation doesn't make sense. e.g.
            multiplying a numeric value with a TEXT response value.

        """
        return self._calculate_new_val(other, lambda self, other: self * other)

    def __truediv__(self, other: object) -> float:
        """
        Divide the response value represented by the current instance
        of RedcapNumber by another object.

        This method performs division between the response value and
        another object. Unlike the comparison operations, REDCap will
        coerce number-like strings to their numeric values when
        performing arithmetic operations. e.g.
            - RedcapNumber("13") /  1   => 13
            - RedcapNumber("13") / "1"  => 13

        Parameters
        ----------
        other : object
            The object to divide the response value by.

        Returns
        -------
        float
            The result of the division. Returns np.nan if the operation
            is done on objects of valid type (i.e. str, float, etc.),
            but the operation doesn't make sense. e.g. dividing a
            TEXT response value with a numeric value.

        """
        return self._calculate_new_val(other, lambda self, other: self / other)

    # TODO: Check 12.0 + 1
    # Complains about too many return statements (7 > 6), but I think it's fine
    def _calculate_new_val(self, other: object, calc_func: Callable) -> float:  # NOQA: PLR0911
        """
        Perform an arithmetic operation between the response value
        represented by the current instance of RedcapNumber and another
        object.

        Unlike the comparison operations, REDCap will coerce number-like
        strings to their numeric values when performing arithmetic
        operations with them. e.g.
            - RedcapNumber("12") +  1   => 13
            - RedcapNumber("12") + "1"  => 13

        TEXT-like response values have a numeric value of np.nan, so any
        arithmetic operations performed with them will return np.nan.
        MISSING response values have a numeric value of 0.0, thus can be
        involved in arithmetic operations with other NUMBER and MISSING
        category response values.

        Parameters
        ----------
        other : object
            The object to perform the arithmetic operation with.
        calc_func : Callable
            The arithmetic function to be used for the operation.
            e.g. self + other, self / other, etc.

        Returns
        -------
        float
            The result of the arithmetic operation.
            Returns np.nan if the operation is done on objects of valid
            type (i.e. str, float, etc.), but the operation doesn't make
            sense. e.g. dividing a TEXT response value with a numeric.

            NotImplemented is returned if the operation is performed on
            unsupported types, but this should never happen due to the
            guard clause in the _validate_other() method.

            NotImplemented is also returned if the operation is done on
            a response value of category other than TEXT, MISSING, or
            NUMBER, but this category does not exist yet, and thus this
            should never happen.

        Raises
        ------
        ZeroDivisionError
            MISSING response values always have a numeric value of 0.0
            NUMBER-like response values can also have a numeric value of
            0.0. Thus, division using these values is invalid.

        """
        self._validate_other(other)

        match self._dtype:
            # Arithmetic with TEXT values always returns np.nan
            case RCNDtype.TEXT:
                return np.nan
            # MISSING and NUMBER-like values have valid numeric values
            case RCNDtype.MISSING | RCNDtype.NUMBER:
                try:
                    # TEXT-like values have a numeric value of np.nan, thus
                    # return np.nan, but other categories are valid.
                    if isinstance(other, RedcapNumber):
                        return (
                            np.nan
                            if other.dtype == RCNDtype.TEXT
                            else calc_func(self.num_val, other.num_val)
                        )
                    # Number-like strings are coerced to their numeric values,
                    # so we attempt the same, and return np.nan if it fails.
                    if isinstance(other, str):
                        return (
                            calc_func(self.num_val, float(other))
                            if self._is_numeric_str(other)
                            else np.nan
                        )
                    # Numeric values are valid for arithmetic operations
                    if isinstance(other, float | int):
                        return calc_func(self.num_val, other)
                except ZeroDivisionError:
                    return np.nan
                else:
                    return NotImplemented
            case _:
                return NotImplemented

    def _is_numeric_str(self, input_str: str) -> bool:
        """
        Check if the input string represents a valid numeric value.

        This method attempts to convert the input string to a float to
        determine if it represents a numeric value.

        Parameters
        ----------
        input_str : str
            The input string to check.

        Returns
        -------
        bool
            True if the input string represents a valid numeric value,
            False otherwise.

        """
        try:
            float(input_str)
        except (OverflowError, TypeError, ValueError):
            return False
        else:
            return True

    # TODO: Investigate if returning NotImplemented is a better approach
    def _validate_other(self, other: object) -> None:
        """
        Validate the type of the other object for comparison or
        arithmetic operations.

        This method checks if the other object is of a supported type
        for comparison or arithmetic operations with a RedcapNumber.
        Supported types are RedcapNumber, str, float, and int.

        Parameters
        ----------
        other : object
            The object to validate.

        Raises
        ------
        NotImplementedError
            Raises an exception instead of returning NotImplemented if
            the other object is of an unsupported type because I wanted
            to avoid potential issues with Python's default behaviour.
            i.e. String concatenation for addition between 2 strings.
            However, I don't know if this is the recommended approach or
            even a valid concern.

        """
        if not isinstance(other, RedcapNumber | str | float | int):
            err_str = f"Unsupported operation between RedcapNumber and {type(other)}!"  # NOQA: E501
            raise NotImplementedError(err_str)


@register_extension_dtype
class RedcapNumberDtype(PandasExtensionDtype):
    """
    An extension dtype for representing REDCap-style response values in
    pandas DataFrames and Series.

    This dtype is designed to allow data from REDCap stored in pandas
    data structures to mimic REDCap's internal handling of response
    values. i.e. Data is stored as strings internally, but can be
    coerced to numeric values depending on context.

    Attributes
    ----------
    name : str
        The name of the custom dtype ("rc_num"). This is used for
        identifying the dtype within pandas operations. e.g.
            - pd.array(["1", "2", "3"], dtype="rc_num")
            - pd.Series(["1", "2", "3"], dtype="rc_num")
            - Series.astype("rc_num")

    type : type
        The scalar type associated with this dtype ("RedcapNumber").

    Methods
    -------
    __str__() -> str
        Returns the name of the custom dtype.
    _is_numeric() -> bool
        Specifies that the dtype is numeric for some pandas operations.
    construct_array_type() -> type[RedcapNumberArray]
        Returns the array type associated with this dtype, which is
        RedcapNumberArray.

    """

    name = "rc_num"
    type = RedcapNumber

    def __str__(self) -> str:
        """Returns the name of the custom dtype."""
        return self.name

    @property
    def _is_numeric(self) -> bool:
        """Specifies that the dtype is numeric."""
        return True

    @classmethod
    def construct_array_type(cls) -> "type[RedcapNumberArray]":
        """
        Returns the array type associated with this dtype.

        Returns
        -------
        type[RedcapNumberArray]
            The `RedcapNumberArray` class associated with this dtype.

        """
        return RedcapNumberArray


class RedcapNumberArray(ExtensionArray):
    # From pandas/_typing.py
    # Here so Pylance stops complaining about types in self.take()
    TakeIndexer: TypeAlias = (
        Sequence[int] | Sequence[np.integer] | npt.NDArray[np.integer]
    )

    def __init__(
        self,
        num_values: Iterable[float],
        str_values: Iterable[str],
        dtype_strings: Iterable[RCNDtype],
        copy: bool = False,
    ) -> None:
        self.num_values = np.asarray(num_values, dtype=np.float64)
        self.str_values = np.asarray(str_values, dtype=object)
        self.dtypes = np.asarray(dtype_strings, dtype=object)

    @classmethod
    def _from_sequence(
        cls,
        scalars: Iterable[str],
        *,
        dtype: str | None = None,  # NOQA: ARG003
        copy: bool = False,  # NOQA: ARG003
    ) -> "RedcapNumberArray":
        num_values, str_values, dtype_strings = zip(
            *[
                (
                    RedcapNumber(val).num_val,
                    RedcapNumber(val).str_val,
                    RedcapNumber(val).dtype,
                )
                for val in scalars
            ],
            strict=True,
        )
        return RedcapNumberArray(
            num_values,
            str_values,
            dtype_strings,
        )

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
                    self.dtypes[item],
                )
            case _:
                err_str = f"Invalid index type, expected int or slice but got {type(item)}"  # NOQA: E501
                raise TypeError(err_str)

    def __len__(self) -> int:
        return self.num_values.size

    @property
    def dtype(self) -> RedcapNumberDtype:
        return RedcapNumberDtype()

    @property
    def nbytes(self) -> int:
        return (
            self.num_values.nbytes
            + self.str_values.nbytes
            + self.dtypes.nbytes
        )

    def isna(self) -> np.ndarray:
        return np.isnan(self.num_values)

    def copy(self) -> "RedcapNumberArray":
        return RedcapNumberArray(
            np.copy(self.num_values),
            np.copy(self.str_values),
            np.copy(self.dtypes),
        )

    # Pylance complains that this method returns a np.ndarray instead of a bool
    # like the superclass __eq__ method, but this is the correct return type
    # according to the pandas documentation.
    # See: pandas/core/arrays/base.py where the devs ignore the same error.
    def __eq__(self, other: object) -> np.ndarray:  # type: ignore[reportIncompatibleMethodOverride]
        if not isinstance(other, RedcapNumber | str | float | int):
            return NotImplemented

        missing_mask = self.dtypes == RCNDtype.MISSING
        text_mask = self.dtypes == RCNDtype.TEXT
        number_mask = self.dtypes == RCNDtype.NUMBER

        result = np.empty(self.num_values.size, dtype=bool)

        if isinstance(other, RedcapNumber):
            result = (
                np.where(missing_mask, self._is_other_eq_missing(other), False)  # NOQA: FBT003
                | np.where(text_mask, self.str_values == other.str_val, False)  # NOQA: FBT003
                | np.where(number_mask, self.str_values == other.str_val, False)  # NOQA: FBT003, E501
            )
        elif isinstance(other, str):
            result = (
                np.where(missing_mask, other == "", False)  # NOQA: FBT003
                | np.where(text_mask, self.str_values == other, False)  # NOQA: FBT003
                | np.where(number_mask, self.str_values == other, False)  # NOQA: FBT003
            )
        elif isinstance(other, float | int):
            result = (
                np.where(missing_mask, other == 0.0, False)  # NOQA: FBT003
                | np.where(text_mask, False, False)  # NOQA: FBT003
                | np.where(number_mask, self.num_values == other, False)  # NOQA: FBT003
            )

        return result

    def _is_other_eq_missing(
        self,
        other: "RedcapNumber | str | float",
    ) -> bool:
        match other:
            case RedcapNumber():
                return any(
                    (
                        other.dtype == RCNDtype.MISSING,
                        other.str_val == "",
                        other.num_val == 0.0,
                    ),
                )
            case str():
                return other == ""
            case float() | int():
                return other == 0.0
            case _:
                return NotImplemented


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
        dtype_strings = take(
            self.dtypes,
            indices,
            allow_fill=allow_fill,
            fill_value=fill_value,
        )

        return RedcapNumberArray(num_values, str_values, dtype_strings)

    @classmethod
    def _concat_same_type(
        cls,
        to_concat: Iterable["RedcapNumberArray"],
    ) -> "RedcapNumberArray":
        return RedcapNumberArray(
            np.concatenate([arr.num_values for arr in to_concat]),
            np.concatenate([arr.str_values for arr in to_concat]),
            np.concatenate([arr.dtypes for arr in to_concat]),
        )

    # TODO: Fix these methods so that they return RedcapNumberArray objects
    def __lt__(self, other: object) -> np.ndarray:
        return self._compare(other, lambda self, other: self < other)

    def __le__(self, other: object) -> np.ndarray:
        return self._compare(other, lambda self, other: self <= other)

    def __gt__(self, other: object) -> np.ndarray:
        return self._compare(other, lambda self, other: self > other)

    def __ge__(self, other: object) -> np.ndarray:
        return self._compare(other, lambda self, other: self >= other)

    def _compare(self, other: object, comp_func: Callable) -> np.ndarray:
        if isinstance(other, RedcapNumber | str | float | int):
            return self._compare_scalar(other, comp_func)

        if isinstance(other, list | tuple | np.ndarray | pd.Series):
            return self._compare_sequence(other, comp_func)

        return NotImplemented

    def _compare_scalar(
        self,
        other: RedcapNumber | str | float,
        comp_func: Callable,
    ) -> np.ndarray:
        match other:
            case RedcapNumber() | str():
                other_val = (
                    other.str_val if isinstance(other, RedcapNumber) else other
                )
                return comp_func(self.str_values, other_val)
            case float() | int():
                return comp_func(self.num_values, other)
            case _:
                return NotImplemented

    def _compare_sequence(
        self,
        other: list | tuple | np.ndarray | pd.Series,
        comp_func: Callable,
    ) -> np.ndarray:
        if len(other) != len(self):
            err_str = "Comparison between a RedcapNumberArray and Sequence is only supported for objects with equal length!"  # NOQA: E501
            raise ValueError(err_str)

        result = np.empty(self.num_values.size, dtype=bool)

        for idx, val in enumerate(other):
            match val:
                case RedcapNumber() | str():
                    result[idx] = comp_func(
                        self.str_values[idx],
                        val.str_val if isinstance(val, RedcapNumber) else val,
                    )
                case float() | int():
                    result[idx] = comp_func(self.num_values[idx], val)
                case _:
                    return NotImplemented

        return result

    def __add__(self, other: object) -> "RedcapNumberArray":
        return self._calculate(other, lambda self, other: self + other)

    def __sub__(self, other: object) -> "RedcapNumberArray":
        return self._calculate(other, lambda self, other: self - other)

    def __mul__(self, other: object) -> "RedcapNumberArray":
        return self._calculate(other, lambda self, other: self * other)

    def __truediv__(self, other: object) -> "RedcapNumberArray":
        return self._calculate(other, lambda self, other: self / other)

    def _calculate(
        self,
        other: object,
        calc_func: Callable,
    ) -> "RedcapNumberArray":
        if isinstance(other, RedcapNumber | str | float | int):
            return self._calculate_scalar(other, calc_func)

        if isinstance(other, list | tuple | np.ndarray | pd.Series):
            return self._calculate_sequence(other, calc_func)

        return NotImplemented

    def _calculate_scalar(
        self,
        other: RedcapNumber | str | float,
        calc_func: Callable,
    ) -> "RedcapNumberArray":
        other_dtype = self._determine_dtype(other)

        if other_dtype == RCNDtype.TEXT:
            num_values = np.array(
                [np.nan] * self.num_values.size, dtype=np.float64
            )
            str_values = np.array(
                ["$$CALC_ERR"] * self.num_values.size, dtype=object
            )
            dtypes = np.array(
                [RCNDtype.TEXT] * self.num_values.size, dtype=object
            )
            return RedcapNumberArray(num_values, str_values, dtypes)

        other_val = float(other) if other_dtype == RCNDtype.NUMBER else 0.0

        num_values = np.empty(self.num_values.size, dtype=np.float64)
        str_values = np.empty(self.str_values.size, dtype=object)
        dtypes = np.empty(self.dtypes.size, dtype=object)
        for idx, dtype in enumerate(self.dtypes):
            if dtype == RCNDtype.TEXT:
                num_values[idx] = np.nan
                str_values[idx] = "$$CALC_ERR"
                dtypes[idx] = RCNDtype.TEXT
            else:
                try:
                    num_value = calc_func(self.num_values[idx], other_val)
                except ZeroDivisionError:
                    num_values[idx] = np.nan
                    str_values[idx] = "$$CALC_ERR"
                    dtypes[idx] = RCNDtype.TEXT
                else:
                    num_values[idx] = num_value
                    str_values[idx] = str(num_value)
                    dtypes[idx] = (
                        RCNDtype.MISSING
                        if (
                            other_dtype == RCNDtype.MISSING
                            and self.dtypes[idx] == RCNDtype.MISSING
                        )
                        else RCNDtype.NUMBER
                    )

        return RedcapNumberArray(num_values, str_values, dtypes)

    def _calculate_sequence(
        self,
        other: list | tuple | np.ndarray | pd.Series,
        calc_func: Callable,
    ) -> "RedcapNumberArray":
        if len(other) != len(self):
            err_str = "Arithmetic operations between a RedcapNumberArray and Sequence is only supported for objects with equal length!"  # NOQA: E501
            raise ValueError(err_str)

        num_values = np.empty(self.num_values.size, dtype=np.float64)
        str_values = np.empty(self.str_values.size, dtype=object)
        dtypes = np.empty(self.dtypes.size, dtype=object)

        for idx, (self_val, self_dtype, other_val) in enumerate(
            zip(self.num_values, self.dtypes, other, strict=True),
        ):
            other_dtype = self._determine_dtype(other_val)

            other_num = None
            if other_dtype in (RCNDtype.NUMBER, RCNDtype.MISSING):
                other_num = (
                    float(other_val) if other_dtype == RCNDtype.NUMBER else 0.0
                )

            match (self_dtype, other_dtype):
                case (_, RCNDtype.TEXT):
                    num_values[idx] = np.nan
                    str_values[idx] = "$$CALC_ERR"
                    dtypes[idx] = RCNDtype.TEXT
                case (RCNDtype.TEXT, _):
                    num_values[idx] = np.nan
                    str_values[idx] = "$$CALC_ERR"
                    dtypes[idx] = RCNDtype.TEXT
                case (RCNDtype.MISSING, RCNDtype.MISSING):
                    num_values[idx] = 0.0
                    str_values[idx] = ""
                    dtypes[idx] = RCNDtype.MISSING
                case (
                    RCNDtype.MISSING
                    | RCNDtype.NUMBER,
                    RCNDtype.MISSING
                    | RCNDtype.NUMBER,
                ):
                    try:
                        num_value = calc_func(self_val, other_num)
                    except ZeroDivisionError:
                        num_values[idx] = np.nan
                        str_values[idx] = "$$CALC_ERR"
                        dtypes[idx] = RCNDtype.TEXT
                    else:
                        num_values[idx] = num_value
                        str_values[idx] = str(num_value)
                        dtypes[idx] = (
                            RCNDtype.MISSING
                            if self_dtype == RCNDtype.MISSING
                            and other_dtype == RCNDtype.MISSING
                            else RCNDtype.NUMBER
                        )

        return RedcapNumberArray(num_values, str_values, dtypes)

    def _determine_dtype(self, other: RedcapNumber | str | float) -> RCNDtype:
        match other:
            case RedcapNumber():
                return other.dtype
            case int() | float():
                return RCNDtype.NUMBER
            case str():
                try:
                    float(other)
                except (OverflowError, TypeError, ValueError):
                    return RCNDtype.TEXT
                else:
                    return RCNDtype.NUMBER
            case _:
                return NotImplemented
