import re
from typing import ClassVar

import pandas as pd

from pycap_mfr.data.config.config import EMBEDDED_FIELDS_LIT
from pycap_mfr.data_loader.data_loader import DataLoader
from pycap_mfr.data_transformer.data_transformer import DataTransformer


class DataFrameDataTransformer(DataTransformer):
    _instances: ClassVar[dict[int, "DataFrameDataTransformer"]] = {}
    _EMBEDDED_FIELDS_PATT = re.compile(EMBEDDED_FIELDS_LIT)

    def __init__(self, data_loader: DataLoader) -> None:
        if not hasattr(self, "_initialized"):
            self._data_loader = data_loader
            self._data_structs = {}
            self._initialized = True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DataFrameDataTransformer)
            and self._data_loader == other._data_loader
        )

    # Arbitrary constant (13) to make the hash unique from the DataLoader hash
    def __hash__(self) -> int:
        return hash(self._data_loader) + 13

    def __new__(cls, data_loader: DataLoader) -> "DataFrameDataTransformer":
        data_loader_hash = hash(data_loader)
        if data_loader_hash not in cls._instances:
            df_transformer = super().__new__(cls)
            cls._instances[data_loader_hash] = df_transformer
        return cls._instances[data_loader_hash]

    @classmethod
    def get_instance(
        cls,
        data_loader: DataLoader,
    ) -> "DataFrameDataTransformer":
        data_loader_hash = hash(data_loader)
        if data_loader_hash not in cls._instances:
            return cls(data_loader)
        return cls._instances[data_loader_hash]

    def get_missing_data_codes(self) -> list[str]:
        if "missing_data_codes" not in self._data_structs:
            dff = self._data_loader.get_project_info_df()
            self._data_structs["missing_data_codes"] = [
                code.split(",")[0]
                for code in dff.loc[:, "missing_data_codes"][0].split(" | ")
            ]
        return self._data_structs["missing_data_codes"]

    def get_checkbox_fields_list(self) -> list[str]:
        if "checkbox_fields_list" not in self._data_structs:
            dff = self._data_loader.get_field_names_df()
            self._data_structs["checkbox_fields_list"] = dff.loc[
                dff["field_type"] == "checkbox",
                "field_name",
            ].tolist()
        return self._data_structs["checkbox_fields_list"]

    def get_checkbox_fields_dict(self) -> dict[str, list[str]]:
        if "checkbox_fields_dict" not in self._data_structs:
            dff = self._data_loader.get_field_names_df()
            self._data_structs["checkbox_fields_dict"] = (
                dff.loc[
                    dff["original_field_name"].isin(
                        self.get_checkbox_fields_list(),
                    )
                ]
                .groupby("original_field_name")["export_field_name"]
                .apply(list)
                .to_dict()
            )
        return self._data_structs["checkbox_fields_dict"]

    def get_field_names(self) -> dict[str, str]:
        if "field_names" not in self._data_structs:
            dff = self._data_loader.get_field_names_df()
            dff.loc[dff["choice_value"] != "", "logic_str_field_name"] = (
                dff["original_field_name"] + "(" + dff["choice_value"] + ")"
            )
            self._data_structs["field_names"] = (
                dff[dff["logic_str_field_name"] != ""]
                .set_index("logic_str_field_name")["export_field_name"]
                .to_dict()
            )
        return self._data_structs["field_names"]

    def get_conditional_fields_dict(self) -> dict[str, str]:
        if "conditional_fields" not in self._data_structs:
            dff = (
                self._data_loader.get_metadata_df()
                .loc[:, ["field_name", "branching_logic"]]
                .replace("", pd.NA)
            )
            self._data_structs["conditional_fields"] = (
                dff[dff["branching_logic"].notna()]
                .set_index("field_name")
                .to_dict()["branching_logic"]
            )
        return self._data_structs["conditional_fields"]

    def get_embedded_fields_dict(self) -> dict[str, str]:
        raise NotImplementedError
