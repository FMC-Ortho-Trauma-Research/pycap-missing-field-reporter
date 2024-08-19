import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from pycap_missing_reporter.config import DATA_DIR
from pycap_missing_reporter.redcap_facade import REDCapFacade


def _load_env_vars(dev: bool | None = False) -> None:
    if dev:
        load_dotenv(".dev.env")
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

    api_key = args.api_key
    api_url = args.api_url

    if api_key in os.environ:
        api_key = os.getenv(api_key)

    if api_url is None:
        api_url = os.getenv("REDCAP_API_URL")

    if api_key is None:
        error_str = "Error: Missing required API Key."
        raise ValueError(error_str)

    if api_url is None:
        error_str = "Error: Missing required API URL."
        raise ValueError(error_str)

    redcap_facade = REDCapFacade.get_instance(api_url, api_key)
    redcap_facade.save_dataframes_to_csv()

    

if __name__ == "__main__":
    main()
