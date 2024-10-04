from functools import cache
from pathlib import Path

import pandas as pd

from dqm.config import (
    DATA_DIR,
    DEFAULT_PYCAP_EXPORT_KWARGS,
    DF_COLUMN_NAMES,
    DF_NAMES,
 )
from dqm.data_loader.idata_loader import IDataLoader


class CsvDataLoader(IDataLoader):
    def __init__(
        self,
        study_name: str,
        source_dir: Path | None = None,
    ) -> None:
        self._validate_params(study_name, source_dir)
        self._study_name = study_name
        self._source_dir = source_dir if source_dir else DATA_DIR / "raw"

    @staticmethod
    def _validate_params(study_name: str, source_dir: Path | None) -> None:
        if not isinstance(study_name, str):
            err_str = "Param: study_name must be of type str!"
            raise TypeError(err_str)

        if source_dir:
            if not isinstance(source_dir, Path):
                err_str = "Param: source_dir must be of type Path!"
                raise TypeError(err_str)

            if not source_dir.is_dir():
                err_str = "Param: source_dir must be a valid directory!"
                raise NotADirectoryError(err_str)

    @property
    def study_name(self) -> str:
        return self._study_name

    @property
    def source_dir(self) -> Path:
        return self._source_dir

    @property
    def field_mapping(self) -> pd.DataFrame:
        return self._load_data("field_mapping", self.source_dir)

    @property
    def field_metadata(self) -> pd.DataFrame:
        return self._load_data("field_metadata", self.source_dir)

    @property
    def form_mapping(self) -> pd.DataFrame:
        return self._load_data("form_mapping", self.source_dir)

    @property
    def project_data(self) -> pd.DataFrame:
        return self._load_data("project_data", self.source_dir)

    @property
    def study_data(self) -> pd.DataFrame:
        return self._load_data("study_data", self.source_dir)

    @staticmethod
    @cache
    def _load_data(df_name: str, source_dir: Path) -> pd.DataFrame:
        file_path = source_dir / f"{df_name}.csv"
        if not file_path.is_file():
            err_str = f"File not found: {file_path}"
            raise FileNotFoundError(err_str)
        try:
            dff = pd.read_csv(
                file_path,
                **DEFAULT_PYCAP_EXPORT_KWARGS["df_kwargs"],
            )
            if df_name == "study_data":
                return dff
            return dff.loc[:, DF_COLUMN_NAMES[df_name]]
        except Exception as e:
            err_str = f"Error loading data from file: {file_path}"
            raise RuntimeError(err_str) from e

    def save_to_file(
        self, df_name: str, export_path: Path = DATA_DIR / "export",
    ) -> None:
        if df_name not in DF_NAMES:
            err_str = f"Invalid df_name param: {df_name}!"
            raise AttributeError(err_str)
        if not export_path.is_dir():
            err_str = f"Invalid export directory: {export_path}"
            raise NotADirectoryError(err_str)
        try:
            getattr(self, df_name).to_csv(
                export_path / f"{df_name}.csv",
                index=False,
             )
        except Exception as e:
            err_str = f"Error saving file: {export_path / f'{df_name}.csv'}"
            raise RuntimeError(err_str) from e
