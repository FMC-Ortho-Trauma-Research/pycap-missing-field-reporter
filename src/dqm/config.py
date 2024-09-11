from pathlib import Path
from types import MappingProxyType

ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"

DEFAULT_PYCAP_EXPORT_KWARGS = {
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
        "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
     },
    "form_mapping": {
        "export_method": "export_instrument_event_mappings",
        "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
    },
    "field_names": {
        "export_method": "export_field_names",
        "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
    },
    "metadata": {
        "export_method": "export_metadata",
        "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
    },
    "study_data": {
        "export_method": "export_records",
        "export_kwargs": {
            **DEFAULT_PYCAP_EXPORT_KWARGS,
            "export_data_access_groups": True,
         },
    },
}
REDCAP_EXPORT_CONFIG = MappingProxyType(_REDCAP_EXPORT_CONFIG)

DF_NAMES = tuple(_REDCAP_EXPORT_CONFIG.keys())
