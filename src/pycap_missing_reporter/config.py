from pathlib import Path

DATA_DIR = Path(__file__).parent.resolve() / "data"
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

DEFAULT_EXPORT_KWARGS = {
    "format_type": "df",
    "df_kwargs": {
        "index_col": False,
        "dtype": str,
        "na_filter": False,
    },
}

DF_NAMES = [
    "project_info",
    "form_mapping",
    "field_names",
    "metadata",
    "study_data",
]

METADATA_COLS = [
    "field_name",
    "form_name",
    "field_type",
    "field_label",
    "select_choices_or_calculations",
    "branching_logic",
]
