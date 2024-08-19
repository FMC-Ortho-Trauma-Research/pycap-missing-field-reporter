import os
from pathlib import Path
from typing import ClassVar

from redcap.project import Project

from pycap_missing_reporter.config import DATA_DIR, DEFAULT_EXPORT_KWARGS


class REDCapFacade:
    _instances: ClassVar[dict[str, "REDCapFacade"]] = {}

    def __init__(self, api_url: str, api_key: str) -> None:
        if api_key not in REDCapFacade._instances:
            project = Project(api_url, api_key)
            self._get_dataframes(project)
            REDCapFacade._instances[api_key] = self

    @classmethod
    def get_instance(cls, api_url: str, api_key: str) -> "REDCapFacade":
        if api_key not in cls._instances:
            return cls(api_url, api_key)
        return cls._instances[api_key]

    def _get_dataframes(self, project: "Project") -> None:
        self.project_info_df = project.export_project_info(
            **DEFAULT_EXPORT_KWARGS,
        )

        self.form_mapping_df = project.export_instrument_event_mappings(
            **DEFAULT_EXPORT_KWARGS,
        )

        self.field_names_df = project.export_field_names(
            **DEFAULT_EXPORT_KWARGS,
        )

        self.metadata_df = project.export_metadata(
            **DEFAULT_EXPORT_KWARGS,
        )

        export_study_data_kwargs = DEFAULT_EXPORT_KWARGS.copy()
        export_study_data_kwargs.update(
            {"export_data_access_groups": True},
        )
        self.study_data_df = project.export_records(
            **export_study_data_kwargs,
        )

    def save_dataframes_to_csv(self, export_dir: Path = DATA_DIR / "export") -> None:
        os.makedirs(export_dir, exist_ok=True)

        self.project_info_df.to_csv( export_dir / "project_info.csv", index=False)
        self.form_mapping_df.to_csv(export_dir / "form_mapping.csv", index=False)
        self.field_names_df.to_csv(export_dir / "field_names.csv", index=False)
        self.metadata_df.to_csv(export_dir / "metadata.csv", index=False)
        self.study_data_df.to_csv(export_dir / "study_data.csv", index=False)
