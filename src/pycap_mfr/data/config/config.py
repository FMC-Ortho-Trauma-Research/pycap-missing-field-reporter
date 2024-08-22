from pathlib import Path
from types import MappingProxyType

DATA_DIR = Path(__file__).parent.parent.resolve()
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

DEFAULT_EXPORT_KWARGS = {
    "format_type": "df",
    "df_kwargs": {
        "index_col": False,
        "dtype": str,
        "na_filter": False,
    },
}

_REDCAP_EXPORT_CONFIG = {
    "project_info": {
        "export_method": "export_project_info",
        "export_kwargs": DEFAULT_EXPORT_KWARGS,
     },
    "form_mapping": {
        "export_method": "export_instrument_event_mappings",
        "export_kwargs": DEFAULT_EXPORT_KWARGS,
    },
    "field_names": {
        "export_method": "export_field_names",
        "export_kwargs": DEFAULT_EXPORT_KWARGS,
    },
    "metadata": {
        "export_method": "export_metadata",
        "export_kwargs": DEFAULT_EXPORT_KWARGS,
    },
    "study_data": {
        "export_method": "export_records",
        "export_kwargs": {
            **DEFAULT_EXPORT_KWARGS,
            "export_data_access_groups": True,
         },
    },
}
REDCAP_EXPORT_CONFIG = MappingProxyType(_REDCAP_EXPORT_CONFIG)

_METADATA_COLS = [
    "field_name",
    "form_name",
    "field_type",
    "field_label",
    "select_choices_or_calculations",
    "branching_logic",
]
