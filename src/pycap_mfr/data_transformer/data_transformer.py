from abc import ABC, abstractmethod


class DataTransformer(ABC):

    @abstractmethod
    def get_missing_data_codes(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_checkbox_fields_list(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_checkbox_fields_dict(self) -> dict[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def get_field_names(self) -> dict[str, str]:
        raise NotImplementedError
