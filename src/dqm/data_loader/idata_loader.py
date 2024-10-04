from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class IDataLoader(ABC):

    @abstractmethod
    def __init__(self, study_name: str, **kwargs: (Path | None) | str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def study_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def field_mapping(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    @abstractmethod
    def field_metadata(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    @abstractmethod
    def form_mapping(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    @abstractmethod
    def project_data(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    @abstractmethod
    def study_data(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def save_to_file(self, df_name: str, export_path: Path) -> None:
        raise NotImplementedError
