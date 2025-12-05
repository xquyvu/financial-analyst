from logging import getLogger
from typing import Any

import numpy as np
import pandas as pd

logger = getLogger(__name__)


def compute_extraction_accuracy(
    data: pd.DataFrame,
    expected_value_col="expected_value",
    extracted_value_col="extracted_value",
) -> float:
    """
    Compares expected_value and extracted_value objects of the DataFrame and returns a
    extraction_accuracy score. This method compares the values of objects and calculates
    a extraction_accuracy score based on the proportion of the extracted values that are
    correct.

    Args:
        data (DataFrame): DataFrame containing the expected_value and extracted_value columns.
    Returns:
        float: A extraction_accuracy score between 0 and 1, where 1 indicates identical values and
            0 indicates completely different values. Returns NaN if the JSON objects are
            empty.
    """
    expected: pd.Series = data[expected_value_col]  # type: ignore[reportUnknownVariableType]
    extracted: pd.Series = data[extracted_value_col]  # type: ignore[reportUnknownVariableType]

    return np.logical_or(
        expected == extracted,
        expected.isna()
        # When both expected and extracted values are None, we want them to be equal
        & extracted.isna(),
    ).mean()


def compute_precision(
    data: pd.DataFrame,
    expected_value_col="expected_value",
    extracted_value_col="extracted_value",
) -> float:
    """
    Compares expected_value and extracted_value objects of the DataFrame and returns an
    precision score based on value changes. This method compares the values of objects
    and calculates an precision score based on how many of the values match.

    Args:
        data (DataFrame): DataFrame containing the expected_value and extracted_value columns.
    Returns:
        float: An precision score between 0 and 1, where 1 indicates identical values and
            0 indicates completely different values. Returns NaN if the model answer contains None,
            or if the JSON objects are empty.
    """
    data = data.dropna(subset=[extracted_value_col])  # type: ignore
    return (data[expected_value_col] == data[extracted_value_col]).mean()  # type: ignore


def compute_recall(
    data: pd.DataFrame,
    expected_value_col="expected_value",
    extracted_value_col="extracted_value",
) -> float:
    """
    Compares expected_value and extracted_value objects of the DataFrame and returns a
    recall score. This method compares the values of objects and calculates a recall
    score based on how many among the fields to be extracted as specified in the ground
    truth, were extracted correctly.

    Args:
        data (DataFrame): DataFrame containing the expected_value and extracted_value columns.
    Returns:
        float: A recall score between 0 and 1, where 1 indicates identical values and
            0 indicates completely different values. Returns NaN if the model answer
            contains None, or if the JSON objects are empty.
    """
    filtered_data: pd.DataFrame = data.dropna(subset=[expected_value_col])  # type: ignore
    return (filtered_data[expected_value_col] == filtered_data[extracted_value_col]).mean()  # type: ignore


def exact_match(expected_value: Any, extracted_value: Any) -> int:
    """
    Compares `expected_value` and `extracted_value` and returns 1 if they are equal, otherwise 0.

    The function evaluates equality between numbers (integers and floats) and boolean values.

    Parameters:
    expected_value (Union[float, int, bool]): The expected value.
    extracted_value (Union[float, int, bool]): The extracted value to compare.

    Returns:
    int: 1 if `expected_value` equals `extracted_value`, otherwise 0.

    Examples:
    >>> exact_match(5, 5)
    1  # 5 is equal to 5

    >>> exact_match(3.14, 3.14)
    1  # 3.14 is equal to 3.14

    >>> exact_match(True, True)
    1  # True is equal to True

    >>> exact_match(False, True)
    0  # False is not equal to True

    >>> exact_match(10, 20)
    0  # 10 is not equal to 20

    >>> exact_match(1, True)
    1  # 1 is considered equal to True in Python

    >>> exact_match(0, False)
    1  # 0 is considered equal to False in Python

    >>> exact_match(1.0, True)
    1  # 1.0 is equal to True

    >>> exact_match(0.0, False)
    1  # 0.0 is equal to False

    >>> exact_match(3, 3.0)
    1  # 3 is equal to 3.0 in Python

    >>> exact_match(3, 3.1)
    0  # 3 is not equal to 3.1

    >>> exact_match("hello", "hello")
    1  # "hello" is equal to "hello"

    >>> exact_match("hello", "world")
    0  # "hello" is not equal to "world"
    """

    return np.logical_or(
        expected_value == extracted_value,
        pd.isnull(expected_value) & pd.isnull(extracted_value),  # type: ignore
    )
