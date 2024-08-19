from pathlib import Path

DATA_DIR = Path(__file__).parent.resolve() / "data"

DEFAULT_EXPORT_KWARGS = {
    "format_type": 'df',
    "df_kwargs": {
        "index_col": False,
        "dtype": str,
        "na_filter": False,
     },
 }

