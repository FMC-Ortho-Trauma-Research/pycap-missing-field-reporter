from typing import TypeAlias

import pandas as pd
import pytest

ValidIterables: TypeAlias = tuple[str, ...] | list[str] | set[str]

def get_test_project_info_df() -> pd.DataFrame:
    raise NotImplementedError

def get_test_form_mapping_df() -> pd.DataFrame:
    raise NotImplementedError

def get_test_field_names_df() -> pd.DataFrame:
    raise NotImplementedError

def get_test_metadata_df() -> pd.DataFrame:
    raise NotImplementedError

def get_test_study_data_df() -> pd.DataFrame:
    raise NotImplementedError

@pytest.fixture
def get_test_dataframes(dataframes: ValidIterables) -> dict:
    raise NotImplementedError
