from pathlib import Path
from types import MappingProxyType

DATA_DIR = Path(__file__).parent.resolve() / "data"

DEFAULT_PYCAP_EXPORT_KWARGS = {
    "format_type": "df",
    "df_kwargs": {
        "index_col": False,
        "dtype": str,
        "na_filter": False,
    },
}

REDCAP_EXPORT_CONFIG = MappingProxyType(
    {
        "field_mapping": {
            "export_method": "export_field_names",
            "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
        },
        "field_metadata": {
            "export_method": "export_metadata",
            "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
        },
        "form_mapping": {
            "export_method": "export_instrument_event_mappings",
            "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
        },
        "project_data": {
            "export_method": "export_project_info",
            "export_kwargs": DEFAULT_PYCAP_EXPORT_KWARGS,
        },
        "study_data": {
            "export_method": "export_records",
            "export_kwargs": {
                **DEFAULT_PYCAP_EXPORT_KWARGS,
                "export_data_access_groups": True,
            },
        },
    },
)

DF_NAMES = tuple(REDCAP_EXPORT_CONFIG.keys())

DF_COLUMN_NAMES = {
    "field_mapping": [
        "original_field_name",
        "choice_value",
        "export_field_name",
    ],
    "field_metadata": [
        "field_name",
        "form_name",
        "section_header",
        "field_type",
        "field_label",
        "select_choices_or_calculations",
        "field_note",
        "text_validation_type_or_show_slider_number",
        "text_validation_min",
        "text_validation_max",
        "branching_logic",
        "required_field",
        "field_annotation",
    ],
    "form_mapping": [
        "arm_num",
        "unique_event_name",
        "form",
    ],
    "project_data": [
        "project_id",
        "project_title",
        "in_production",
        "secondary_unique_field",
        "is_longitudinal",
        "has_repeating_instruments_or_events",
        "surveys_enabled",
        "record_autonumbering_enabled",
        "randomization_enabled",
        "missing_data_codes",
    ],
}

ALLOWED_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%m-%d-%Y",
    "%m-%d-%Y %H:%M",
    "%m-%d-%Y %H:%M:%S",
    "%d-%m-%Y",
    "%d-%m-%Y %H:%M",
    "%d-%m-%Y %H:%M:%S",
)

MISSING_DATA_CODES = ()
