from pathlib import Path

import pandas as pd
from redcap.project import Project

from dqm.config import DATA_DIR, DF_NAMES, REDCAP_EXPORT_CONFIG
from dqm.data_loader.data_loader_interface import DataLoaderInterface


class REDCapDataLoader(DataLoaderInterface):
    EXPORT_DIR = DATA_DIR / "export"

    def __init__(
        self,
        study_name: str,
        api_url: str,
        api_token: str,
    ) -> None:
        self._validate_params(study_name, api_url=api_url, api_token=api_token)
        self._study_name = study_name
        self._project = Project(api_url, api_token)
        self._dataframes = {}

    def get_dataframes(
        self,
        dataframes: tuple[str, ...],
    ) -> dict[str, pd.DataFrame]:
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

        df_dict = self._load_dataframes_from_redcap(dataframes)
        self._dataframes.update(df_dict)

        return df_dict

    def save_dataframes_to_csv(
        self,
        export_dir: str | Path | None = None,
     ) -> None:
        if not export_dir:
            export_dir = self.EXPORT_DIR

        if not isinstance(export_dir, str | Path):
            err_str = "Param: 'export_dir' must be of type: str or Path!"
            raise TypeError(err_str)

        if isinstance(export_dir, str):
            export_dir = Path(export_dir)

        if not export_dir.exists():
            if export_dir == self.EXPORT_DIR:
                export_dir.mkdir(parents=True)
            else:
                err_str = f"Directory: {export_dir} does not exist!"
                raise FileNotFoundError(err_str)

        if not export_dir.is_dir():
            err_str = f"Path: {export_dir} is not a directory!"
            raise NotADirectoryError(err_str)

    @property
    def study_name(self) -> str:
        return self._study_name

    @property
    def project(self) -> Project:
        return self._project

    @classmethod
    def _validate_params(cls, study_name: str, **kwargs: str | None) -> None:
        if not isinstance(study_name, str):
            err_str = "Param: 'study_name' must be of type: str!"
            raise TypeError(err_str)
        for key, val in kwargs.items():
            if not isinstance(val, str):
                err_str = f"Param: {key} must be of type: str!"
                raise TypeError(err_str)
        try:
            Project(kwargs["api_url"], kwargs["api_token"])
        except AssertionError as e:
            err_str = "Error while initializing Pycap `Project` object!"
            raise ValueError(err_str) from e

    def _load_dataframes_from_redcap(
        self,
        dataframes: tuple[str, ...],
    ) -> dict[str, pd.DataFrame]:
        result_dict = {}

        for df_name in dataframes:
            try:
                export_method = REDCAP_EXPORT_CONFIG[df_name]["export_method"]
                export_kwargs = REDCAP_EXPORT_CONFIG[df_name]["export_kwargs"]

                dff = getattr(self._project, export_method)(**export_kwargs)
                result_dict[df_name] = dff
            except Exception as e:
                err_str = f"Error while loading dataframe: {df_name} from REDCap!"
                raise SystemError(err_str) from e

            if not (dff.dtypes == "object").all():
                err_str = f"Dataframe: {df_name} contains non-str data types!"
                raise TypeError(err_str)

        return result_dict
