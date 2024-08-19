from typing import ClassVar

from pandas import DataFrame

from pycap_missing_reporter.config import METADATA_COLS
from pycap_missing_reporter.redcap_facade import REDCapFacade


class DataFrameBuilder:
    _instances: ClassVar[dict[REDCapFacade, "DataFrameBuilder"]] = {}

    def __new__(cls, redcap_facade: REDCapFacade) -> "DataFrameBuilder":
        if redcap_facade not in cls._instances:
            data_frame_builder = super().__new__(cls)
            cls._instances[redcap_facade] = data_frame_builder
        return cls._instances[redcap_facade]

    def __init__(self, redcap_facade: REDCapFacade) -> None:
        if not hasattr(self, "_initialized"):
            self._raw_data = redcap_facade.get_dataframes("all")
            self._helper_structs: dict[str, dict | list | DataFrame] = {}
            self._initialized = True

    @classmethod
    def get_instance(cls, redcap_facade: REDCapFacade) -> "DataFrameBuilder":
        if redcap_facade not in cls._instances:
            return cls(redcap_facade)
        return cls._instances[redcap_facade]

    def _make_helper_structs(self) -> None:
        self._make_missing_data_codes_list()
        self._make_checkbox_fields_list()
        self._make_checkbox_fields_dict()
        self._make_field_names_dict()

    def _make_missing_data_codes_list(self) -> None:
        code_list = [
            code.split(",")[0]
            for code in self._raw_data["project_info"]
            .loc[:, "missing_data_codes"][0]
            .split(" | ")
        ]
        self._helper_structs["missing_data_codes"] = code_list

    def _make_checkbox_fields_list(self) -> None:
        dff = self._raw_data["metadata"]
        self._helper_structs["checkbox_fields_list"] = dff.loc[
            dff["field_type"] == "checkbox",
            "field_name",
        ].tolist()

    def _make_checkbox_fields_dict(self) -> None:
        dff = self._raw_data["field_names"]
        self._helper_structs["checkbox_fields_dict"] = (
            dff.loc[
                dff["original_field_name"].isin(
                    self._helper_structs["checkbox_fields_list"],
                )
            ]
            .groupby("original_field_name")["export_field_name"]
            .apply(list)
            .to_dict()
        )

    def _make_field_names_dict(self) -> None:
        dff = self._raw_data["field_names"]
        dff.loc[dff["choice_value"].notna(), "logic_str_field_name"] = (
            dff["original_field_name"]
            + "("
            + dff["choice_value"]
            + ")"
            )
        self._helper_structs["field_names_dict"] = (
            dff[dff["logic_str_field_name"].notna()]
            .set_index("logic_str_field_name")["export_field_name"]
            .to_dict()
         )


    def _clean_dataframes(self) -> None:
        self._clean_metadata()
        self._clean_study_data()

    def _clean_metadata(self) -> None:
        self._raw_data["metadata"] = self._raw_data["metadata"].loc[
            :,
            METADATA_COLS,
        ]

    def _clean_study_data(self) -> None:
        raise NotImplementedError

