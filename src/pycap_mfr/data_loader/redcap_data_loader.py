from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pandas import DataFrame
from redcap.project import Project

from pycap_mfr.data.config.config import DATA_DIR, REDCAP_EXPORT_CONFIG
from pycap_mfr.data_loader.data_loader import DataLoader

if TYPE_CHECKING:
    from pandas import DataFrame


class RedcapDataLoader(DataLoader):
    _EXPORT_DIR: Path = DATA_DIR / "export"
    _instances: ClassVar[dict[str, "RedcapDataLoader"]] = {}

    def __init__(self, api_url: str, api_key: str) -> None:
        if not hasattr(self, "_initialized"):
            self._api_url = api_url
            self._api_key = api_key
            self._dataframes: dict[str, DataFrame] = {}
            self._initialized = True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, RedcapDataLoader)
            and self._api_key == other._api_key
        )

    def __hash__(self) -> int:
        return hash(self._api_key)

    def __new__(cls, api_url: str, api_key: str) -> "RedcapDataLoader":  # NOQA: ARG003
        if api_key not in cls._instances:
            redcap_data_loader = super().__new__(cls)
            cls._instances[api_key] = redcap_data_loader
        return cls._instances[api_key]

    @classmethod
    def get_instance(cls, api_url: str, api_key: str) -> "RedcapDataLoader":
        if api_key not in cls._instances:
            return cls(api_url, api_key)
        return cls._instances[api_key]

    def get_project_info_df(self) -> "DataFrame":
        self._load_data("project_info")
        return self._dataframes["project_info"]

    def get_form_mapping_df(self) -> "DataFrame":
        self._load_data("form_mapping")
        return self._dataframes["form_mapping"]

    def get_field_names_df(self) -> "DataFrame":
        self._load_data("field_names")
        return self._dataframes["field_names"]

    def get_metadata_df(self) -> "DataFrame":
        self._load_data("metadata")
        return self._dataframes["metadata"]

    def get_study_data_df(self) -> "DataFrame":
        self._load_data("study_data")
        return self._dataframes["study_data"]

    def save_to_csv(self) -> None:
        self._load_data("ALL")
        Path.mkdir(self._EXPORT_DIR, parents=True, exist_ok=True)
        for name, df in self._dataframes.items():
            df.to_csv(self._EXPORT_DIR / f"{name}.csv", index=False)

    def _load_data(self, df_name: str) -> None:
        if df_name == "ALL":
            for name in REDCAP_EXPORT_CONFIG:
                if name not in self._dataframes:
                    self._get_dataframes_from_redcap(name)
        elif df_name not in self._dataframes:
            self._get_dataframes_from_redcap(df_name)

    def _get_dataframes_from_redcap(self, df_name: str) -> None:
        project = Project(self._api_url, self._api_key)
        self._dataframes[df_name] = getattr(
            project,
            REDCAP_EXPORT_CONFIG[df_name]["export_method"],
        )(**REDCAP_EXPORT_CONFIG[df_name]["export_kwargs"])
