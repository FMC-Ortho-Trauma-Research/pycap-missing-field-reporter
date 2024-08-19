import argparse
import os
from distutils.util import strtobool

from dotenv import load_dotenv

from pycap_missing_reporter.config import DATA_DIR, ROOT_DIR
from pycap_missing_reporter.dataframe_builder import DataFrameBuilder
from pycap_missing_reporter.redcap_facade import REDCapFacade


def _load_env_vars(dev: bool | None = False) -> None:
    if dev:
        load_dotenv(ROOT_DIR / ".dev.env")
    load_dotenv(DATA_DIR / ".env")

def _init_arg_parser() -> "argparse.ArgumentParser":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--api_key",
        required=True,
        type=str,
        help="""
            API Token string for REDCap project for which to generate
            missing fields report. Accepts study alias string if
            provided in data/.env file.
        """,
    )

    arg_parser.add_argument(
        "--api_url",
        required=False,
        type=str,
        help="""
            URL of REDCap project for which to generate missing fields
            report. Required if not provided in data/.env file.
        """,
    )

    arg_parser.add_argument(
        "--dev",
        required=False,
        action="store_true",
        help="""
            Flag to indicate whether to load env variables from .dev.env
        """,
    )

    return arg_parser

def main() -> None:
    arg_parser = _init_arg_parser()

    args = arg_parser.parse_args()

    _load_env_vars(args.dev)

    cache_results = os.getenv("CACHE_INTERMEDIATE_VALUES")
    use_cache = os.getenv("USE_CACHED_VALUES")

    if not isinstance(cache_results, str):
        cache_results = False
    else:
        cache_results = bool(strtobool(cache_results))

    if not isinstance(use_cache, str):
        use_cache = False
    else:
        use_cache = bool(strtobool(use_cache))

    api_key = args.api_key
    api_url = args.api_url

    if api_key in os.environ:
        api_key = os.getenv(api_key)

    if api_url is None:
        api_url = os.getenv("API_URL")

    if api_key is None:
        error_str = "Error: Missing required API Key."
        raise ValueError(error_str)

    if api_url is None:
        error_str = "Error: Missing required API URL."
        raise ValueError(error_str)

    redcap_facade = REDCapFacade.get_instance(api_url, api_key)

    if use_cache:
        redcap_facade.load_dataframes("cache")
    else:
        redcap_facade.load_dataframes("redcap")

    if cache_results:
        redcap_facade.save_dataframes_to_csv()

    from pprint import pp

    df_builder = DataFrameBuilder.get_instance(redcap_facade)
    df_builder._make_helper_structs()
    pp(df_builder._helper_structs["field_names_dict"])

if __name__ == "__main__":
    main()
