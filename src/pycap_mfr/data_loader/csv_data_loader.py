from pathlib import Path

import pandas as pd
from pandas import DataFrame

from pycap_mfr.data.config.config import (
    DATA_DIR,
    DEFAULT_EXPORT_KWARGS,
    REDCAP_EXPORT_CONFIG,
)
from pycap_mfr.data_loader.data_loader import DataLoader


class CSVDataLoader(DataLoader):
    _CACHE_DIR: Path = DATA_DIR / "cache"
    _DF_NAMES: tuple[str, ...] = tuple(REDCAP_EXPORT_CONFIG.keys())

    def __init__(self, cache_dir: str | None = None) -> None:
        if not hasattr(self, "_initialized"):
            if cache_dir is None:
                self._cache_dir = self._CACHE_DIR
            else:
                self._cache_dir = Path(cache_dir)
            self._dataframes: dict[str, DataFrame] = {}
            self._initialized = True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CSVDataLoader)

    def __hash__(self) -> int:
        return hash(CSVDataLoader)

    def __new__(cls, cache_dir: str | None = None) -> "CSVDataLoader":  # NOQA: ARG003
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, cache_dir: str | None = None) -> "CSVDataLoader":
        if not hasattr(cls, "_instance"):
            return cls(cache_dir)
        return cls._instance

    def get_project_info_df(self) -> DataFrame:
        self._load_data("project_info")
        return self._dataframes["project_info"]

    def get_form_mapping_df(self) -> DataFrame:
        self._load_data("form_mapping")
        return self._dataframes["form_mapping"]

    def get_field_names_df(self) -> DataFrame:
        self._load_data("field_names")
        return self._dataframes["field_names"]

    def get_metadata_df(self) -> DataFrame:
        self._load_data("metadata")
        return self._dataframes["metadata"]

    def get_study_data_df(self) -> DataFrame:
        self._load_data("study_data")
        return self._dataframes["study_data"]

    def save_to_csv(self) -> None:
        return

    def _load_data(self, df_name: str) -> None:
        if df_name == "ALL":
            for name in self._DF_NAMES:
                if name not in self._dataframes:
                    self._get_dataframes_from_csv(name)
        elif df_name not in self._dataframes:
            self._get_dataframes_from_csv(df_name)

    def _get_dataframes_from_csv(self, df_name: str) -> None:
        self._dataframes[df_name] = pd.read_csv(
            self._cache_dir / f"{df_name}.csv",
            **DEFAULT_EXPORT_KWARGS["df_kwargs"],
         )
