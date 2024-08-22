from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class DataLoader(ABC):

    @abstractmethod
    def get_project_info_df(self) -> "DataFrame":
        raise NotImplementedError

    @abstractmethod
    def get_form_mapping_df(self) -> "DataFrame":
        raise NotImplementedError

    @abstractmethod
    def get_field_names_df(self) -> "DataFrame":
        raise NotImplementedError

    @abstractmethod
    def get_metadata_df(self) -> "DataFrame":
        raise NotImplementedError

    @abstractmethod
    def get_study_data_df(self) -> "DataFrame":
        raise NotImplementedError

    @abstractmethod
    def save_to_csv(self) -> None:
        raise NotImplementedError
