from functools import cache
from pathlib import Path

import pandas as pd
from redcap.project import Project

from dqm.config import DATA_DIR, DF_COLUMN_NAMES, REDCAP_EXPORT_CONFIG
from dqm.data_loader.idata_loader import IDataLoader


class RedcapDataLoader(IDataLoader):
    def __init__(
        self,
        study_name: str,
        url: str,
        token: str,
        export_dir: Path | None = None,
    ) -> None:
        self._validate_params(study_name, url, token, export_dir)
        self._study_name = study_name
        self._project = Project(url, token)
        self._export_dir = export_dir if export_dir else DATA_DIR / "export"

    @staticmethod
    def _validate_params(
        study_name: str,
        url: str,
        token: str,
        export_dir: Path | None,
    ) -> None:
        if not all(
            isinstance(param, str)
            for param in (study_name, url, token)
         ):
            err_str = "Params: study_name, url, and token must be of type str!"
            raise TypeError(err_str)
        if export_dir:
            if not isinstance(export_dir, Path):
                err_str = "Param: export_dir must be of type Path!"
                raise TypeError(err_str)
            if not export_dir.is_dir():
                err_str = "Param: export_dir must be a valid directory!"
                raise NotADirectoryError(err_str)

    @property
    def study_name(self) -> str:
        return self._study_name

    @property
    def project(self) -> Project:
        return self._project

    @property
    def export_dir(self) -> Path:
        return self._export_dir

    @property
    def field_mapping(self) -> pd.DataFrame:
        return self._load_data("field_mapping", self.project)

    @property
    def field_metadata(self) -> pd.DataFrame:
        return self._load_data("field_metadata", self.project)

    @property
    def form_mapping(self) -> pd.DataFrame:
        return self._load_data("form_mapping", self.project)

    @property
    def project_data(self) -> pd.DataFrame:
        return self._load_data("project_data", self.project)

    @property
    def study_data(self) -> pd.DataFrame:
        return self._load_data("study_data", self.project)

    def save_to_file(
        self,
        df_name: str,
        export_path: Path | None = None,
    ) -> None:
        if df_name not in REDCAP_EXPORT_CONFIG:
            err_str = f"Invalid DataFrame name: {df_name}"
            raise ValueError(err_str)

        export_path = export_path if export_path else self.export_dir
        if not isinstance(export_path, Path):
            err_str = "Param: export_path must be of type Path!"
            raise TypeError(err_str)

        if not export_path.is_dir():
            err_str = "Param: export_path must be a valid directory!"
            raise NotADirectoryError(err_str)

        dff = getattr(self, df_name)
        dff.to_csv(export_path / f"{df_name}.csv", index=False)

    @staticmethod
    @cache
    def _load_data(df_name: str, pycap_proj: Project) -> pd.DataFrame:
        export_method = REDCAP_EXPORT_CONFIG[df_name]["export_method"]

        # The `export_method` should always be a string, but raise an
        # error here to avoid a weird Pylance error.
        if not isinstance(export_method, str):
            err_str = "Export method must be of type str!"
            raise TypeError(err_str)
        try:
            dff = getattr(pycap_proj, export_method)(
                **REDCAP_EXPORT_CONFIG[df_name]["export_kwargs"],
            )

            if df_name == "study_data":
                return dff
            return dff.loc[:, DF_COLUMN_NAMES[df_name]]
        except Exception as e:
            err_str = f"Error loading {df_name} from REDCap: {e}"
            raise RuntimeError(err_str) from e

