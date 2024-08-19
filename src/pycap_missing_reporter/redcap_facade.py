from pathlib import Path
from typing import ClassVar

import pandas as pd
from pandas import DataFrame
from redcap.project import Project

from pycap_missing_reporter.config import (
    DATA_DIR,
    DEFAULT_EXPORT_KWARGS,
    DF_NAMES,
)


class REDCapFacade:
    _EXPORT_DIR: Path = DATA_DIR / "export"
    _instances: ClassVar[dict[str, "REDCapFacade"]] = {}

    def __new__(cls, api_url: str, api_key: str) -> "REDCapFacade":  # NOQA: ARG003
        if api_key not in cls._instances:
            redcap_facade = super().__new__(cls)
            cls._instances[api_key] = redcap_facade
        return cls._instances[api_key]

    def __init__(self, api_url: str, api_key: str) -> None:
        if not hasattr(self, "_initialized"):
            self._dataframes: dict[str, DataFrame] = {}
            self._api_url = api_url
            self._api_key = api_key
            self._initialized = True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, REDCapFacade) and self._api_key == other._api_key
        )

    def __hash__(self) -> int:
        return hash(self._api_key)

    @classmethod
    def get_instance(cls, api_url: str, api_key: str) -> "REDCapFacade":
        if api_key not in cls._instances:
            return cls(api_url, api_key)
        return cls._instances[api_key]

    def get_dataframes(self, names: list[str] | str) -> dict[str, DataFrame]:
        self.load_dataframes()
        if isinstance(names, str):
            if names.lower() == "all":
                return self._dataframes
            return {names: self._dataframes[names]}
        return {name: self._dataframes[name] for name in names}

    def load_dataframes(self, cache_opt: str = "redcap") -> None:
        if self._dataframes:
            return
        if cache_opt == "cache":
            self._get_dataframes_from_cache()
        if cache_opt == "redcap":
            self._get_dataframes_from_redcap()

    def _get_dataframes_from_redcap(self) -> None:
        project = Project(self._api_url, self._api_key)
        self._dataframes["project_info"] = project.export_project_info(
            **DEFAULT_EXPORT_KWARGS,
        )
        self._dataframes["form_mapping"] = (
            project.export_instrument_event_mappings(
                **DEFAULT_EXPORT_KWARGS,
            )
        )
        self._dataframes["field_names"] = project.export_field_names(
            **DEFAULT_EXPORT_KWARGS,
        )
        self._dataframes["metadata"] = project.export_metadata(
            **DEFAULT_EXPORT_KWARGS,
        )
        export_study_data_kwargs = DEFAULT_EXPORT_KWARGS.copy()
        export_study_data_kwargs.update({"export_data_access_groups": True})
        self._dataframes["study_data"] = project.export_records(
            **export_study_data_kwargs,
        )

    def _get_dataframes_from_cache(
        self, cache_dir: Path = _EXPORT_DIR,
    ) -> None:
        for name in DF_NAMES:
            cache_file = cache_dir / f"{name}.csv"
            if cache_file.exists():
                self._dataframes[name] = pd.read_csv(
                    cache_file,
                    **DEFAULT_EXPORT_KWARGS["df_kwargs"],
                )

        if len(self._dataframes) != len(DF_NAMES):
            raise FileNotFoundError

    def save_dataframes_to_csv(self, export_dir: Path = _EXPORT_DIR) -> None:
        self.load_dataframes()
        Path.mkdir(export_dir, parents=True, exist_ok=True)
        for name, df in self._dataframes.items():
            df.to_csv(export_dir / f"{name}.csv", index=False)
