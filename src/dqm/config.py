from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"

DF_NAMES = (
    "project_info",
    "form_mapping",
    "field_names",
    "metadata",
    "study_data",
 )

DEFAULT_PYCAP_EXPORT_KWARGS = {
    "format_type": "df",
    "df_kwargs": {
        "index_col": False,
        "dtype": str,
        "na_filter": False,
    },
}
