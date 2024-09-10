from pathlib import Path

import pandas as pd

from dqm.config import DATA_DIR
from dqm.data_loader.data_loader_interface import DataLoaderInterface


class REDCapDataLoader(DataLoaderInterface):
    EXPORT_DIR = DATA_DIR / "export"

    def __init__(
        self,
        study_name: str,
        api_url: str | None,
        api_token: str | None,
    ) -> None:
        raise NotImplementedError

    def get_dataframes(
        self,
        dataframes: tuple[str, ...],
    ) -> dict[str, pd.DataFrame]:
        raise NotImplementedError

    def save_dataframes_to_csv(
        self,
        export_dir: str | Path | None = None,
     ) -> None:
        raise NotImplementedError

    @property
    def study_name(self) -> str:
        raise NotImplementedError

    @property
    def api_url(self) -> str:
        raise NotImplementedError

    @property
    def api_token(self) -> str:
        raise NotImplementedError

    @classmethod
    def _validate_params(cls, study_name: str, **kwargs: str | None) -> None:
        raise NotImplementedError

    def _load_dataframes_from_redcap(
        self,
        dataframes: tuple[str, ...],
    ) -> dict[str, pd.DataFrame]:
        raise NotImplementedError

