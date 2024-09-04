import argparse

from dotenv import load_dotenv

from pycap_mfr.data.config.config import DATA_DIR, ROOT_DIR


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
    raise NotImplementedError

if __name__ == "__main__":
    main()
