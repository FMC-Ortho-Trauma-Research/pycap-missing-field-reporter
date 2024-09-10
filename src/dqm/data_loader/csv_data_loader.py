from pathlib import Path

import pandas as pd

from dqm.config import DATA_DIR, DEFAULT_PYCAP_EXPORT_KWARGS, DF_NAMES
from dqm.data_loader.data_loader_interface import DataLoaderInterface


class CSVDataLoader(DataLoaderInterface):
    SOURCE_DIR = DATA_DIR / "raw"

    def __init__(self, study_name: str, source_dir: str | Path | None = None) -> None:
        self._validate_params(study_name=study_name, source_dir=source_dir)
        self._study_name = study_name
        self._source_dir = Path(source_dir) if source_dir else self.SOURCE_DIR

    # TODO: Implement lazy loading of dataframes
    def get_dataframes(self, dataframes: tuple[str, ...]) -> dict[str, pd.DataFrame]:
        if not isinstance(dataframes, tuple):
            err_str = f"Param: dataframes must be of type: tuple[str, ...], not {type(dataframes)}!"
            raise TypeError(err_str)
        if not dataframes:
            err_str = "Param: dataframes must not be an empty tuple!"
            raise ValueError(err_str)
        for df_name in dataframes:
            if not isinstance(df_name, str):
                err_str = f"Value: '{df_name}' must be of type str!"
                raise TypeError(err_str)
            if df_name not in DF_NAMES:
                err_str = f"Value: '{df_name}' is not a valid dataframe name!"
                raise ValueError(err_str)
            if not (source_file := self.source_dir / f"{df_name}.csv").exists():
                err_str = f"File: '{source_file}' does not exist!"
                raise FileNotFoundError(err_str)

        return self._load_dataframes_from_csv(dataframes)

    @property
    def study_name(self) -> str:
        return self._study_name

    @property
    def source_dir(self) -> Path:
        return self._source_dir

    @classmethod
    def _validate_params(cls, study_name: str, source_dir: str | Path | None) -> None:
        if not isinstance(study_name, str):
            err_str = f"Param: study_name must be of type str, not {type(study_name)}!"
            raise TypeError(err_str)

        if source_dir:
            if isinstance(source_dir, str):
                source_dir = Path(source_dir)
            if not source_dir.exists():
                err_str = f"The Path: '{source_dir}' does not exist!"
                raise FileNotFoundError(err_str)
            if not source_dir.is_dir():
                err_str = f"The Path: '{source_dir}' is not a directory!"
                raise NotADirectoryError(err_str)

    # TODO: Implement lazy loading of dataframes
    def _load_dataframes_from_csv(self, dataframes: tuple[str, ...]) -> dict[str, pd.DataFrame]:
        result_dict = {}

        for df_name in dataframes:
            try:
                dff = pd.read_csv(
                    self.source_dir / f"{df_name}.csv",
                    **DEFAULT_PYCAP_EXPORT_KWARGS["df_kwargs"],
                 )
                result_dict[df_name] = dff
            except pd.errors.ParserError as e:
                err_str = f"The file '{df_name}.csv' is not a valid CSV file."
                raise pd.errors.ParserError(err_str) from e

        return result_dict

