from abc import ABC, abstractmethod

import pandas as pd


class DataLoaderInterface(ABC):
    @abstractmethod
    def get_dataframes(
        self, dataframes: tuple[str, ...],
    ) -> dict[str, pd.DataFrame]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _validate_params(cls, study_name: str, **kwargs: str | None) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def study_name(self) -> str:
        raise NotImplementedError
