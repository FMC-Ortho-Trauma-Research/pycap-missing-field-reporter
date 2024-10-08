from pathlib import Path

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from dqm.config import DATA_DIR, DEFAULT_PYCAP_EXPORT_KWARGS
from dqm.data_loader.csv_data_loader import CsvDataLoader

DEFAULT_SOURCE_DIR = DATA_DIR / "raw"

DEFAULT_EXPORT_DIR = DATA_DIR / "export"

TEST_DATA_DIR = Path(__file__).parent.resolve() / "test_data"

DF_KWARGS = DEFAULT_PYCAP_EXPORT_KWARGS["df_kwargs"]

def test_init_success() -> None:
    csvdl = CsvDataLoader("study")

    assert csvdl.study_name == "study"
    assert csvdl.source_dir == DEFAULT_SOURCE_DIR


def test_init_custom_dir_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=True)

    csvdl = CsvDataLoader("study", source_dir=Path("data"))

    assert csvdl.study_name == "study"
    assert csvdl.source_dir == Path("data")


def test_init_invalid_name_type() -> None:
    study_name = object()

    with pytest.raises(TypeError):
        CsvDataLoader(study_name)  # type: ignore[reportArgumentType]


def test_init_invalid_dir_path(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    with pytest.raises(NotADirectoryError):
        CsvDataLoader("study", source_dir=Path("data"))


def test_get_field_mapping_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch(
        "pandas.read_csv",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "field_mapping.csv",
            **DF_KWARGS,
         ),
     )

    dff = csvdl.field_mapping

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()
    assert (
        dff.loc[:, ["original_field_name", "export_field_name"]]
        .eq("")
        .sum()
        .sum()
        == 0
    )
    assert dff.columns.tolist() == [
        "original_field_name",
        "choice_value",
        "export_field_name",
    ]


def test_get_field_metadata_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch(
        "pandas.read_csv",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "field_metadata.csv",
            **DF_KWARGS,
        ),
    )

    dff = csvdl.field_metadata

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()
    assert (
        dff.loc[:, ["field_name", "form_name", "field_type"]]
        .eq("")
        .sum()
        .sum()
        == 0
    )
    assert dff.columns.tolist() == [
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
    ]


# TODO: Figure out if this differs for non-longditudinal projects
def test_get_form_mapping_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch(
        "pandas.read_csv",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "form_mapping.csv",
            **DF_KWARGS,
        ),
    )

    dff = csvdl.form_mapping

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()
    assert dff.eq("").sum().sum() == 0
    assert dff.columns.tolist() == [
        "arm_num",
        "unique_event_name",
        "form",
    ]


def test_get_project_data_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch(
        "pandas.read_csv",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "project_data.csv",
            **DF_KWARGS,
         ),
    )

    dff = csvdl.project_data

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()
    assert (
        dff.loc[
            :,
            [
                "project_id",
                "project_title",
                "in_production",
                "is_longitudinal",
                "has_repeating_instruments_or_events",
                "surveys_enabled",
                "record_autonumbering_enabled",
                "randomization_enabled",
            ],
        ]
        .eq("")
        .sum()
        .sum()
        == 0
    )
    assert dff.columns.tolist() == [
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
    ]


def test_get_study_data_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch(
        "pandas.read_csv",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "study_data.csv",
            **DF_KWARGS,
         ),
    )

    dff = csvdl.study_data

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()


@pytest.mark.parametrize(
    "df_name",
    [
        "field_mapping",
        "field_metadata",
        "form_mapping",
        "project_data",
        "study_data",
    ],
)
def test_modify_data_fail(df_name: str, mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch(
        "dqm.data_loader.csv_data_loader.CsvDataLoader._load_data",
        return_value=pd.DataFrame(),
     )
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()

    new_dff = pd.DataFrame()
    _ = getattr(csvdl, df_name)

    with pytest.raises(AttributeError):
        setattr(csvdl, df_name, new_dff)


@pytest.mark.parametrize(
    "df_name",
    [
        "field_mapping",
        "field_metadata",
        "form_mapping",
        "project_data",
        "study_data",
    ],
)
def test_get_data_missing_data_file(
    mocker: MockerFixture,
    df_name: str,
) -> None:
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch("pathlib.Path.is_file", return_value=False)

    with pytest.raises(FileNotFoundError):
        getattr(csvdl, df_name)


@pytest.mark.parametrize(
    "df_name",
    [
        "field_mapping",
        "field_metadata",
        "form_mapping",
        "project_data",
        "study_data",
    ],
)
def test_get_data_pandas_error(mocker: MockerFixture, df_name: str) -> None:
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pandas.read_csv", side_effect=pd.errors.ParserError)

    with pytest.raises(RuntimeError):
        getattr(csvdl, df_name)


@pytest.mark.parametrize(
    "df_name",
    [
        "field_mapping",
        "field_metadata",
        "form_mapping",
        "project_data",
        "study_data",
    ],
)
def test_save_to_file_success_default_dir(
    mocker: MockerFixture, df_name: str,
) -> None:
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch(
        "dqm.data_loader.csv_data_loader.CsvDataLoader._load_data",
        return_value=pd.DataFrame(),
     )
    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv", return_value=None)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    _ = getattr(csvdl, df_name)

    csvdl.save_to_file(df_name)

    expected_file_path = DEFAULT_EXPORT_DIR / f"{df_name}.csv"
    mock_to_csv.assert_called_once_with(expected_file_path, index=False)


@pytest.mark.parametrize(
    "df_name",
    [
        "field_mapping",
        "field_metadata",
        "form_mapping",
        "project_data",
        "study_data",
    ],
)
def test_save_to_file_success_custom_dir(
    mocker: MockerFixture, df_name: str,
) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch(
        "dqm.data_loader.csv_data_loader.CsvDataLoader._load_data",
        return_value=pd.DataFrame(),
     )
    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv", return_value=None)
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    _ = getattr(csvdl, df_name)

    csvdl.save_to_file(df_name, Path("fake_dir"))

    expected_file_path = Path("fake_dir") / f"{df_name}.csv"
    mock_to_csv.assert_called_once_with(expected_file_path, index=False)


def test_save_to_file_invalid_df_name() -> None:
    csvdl = CsvDataLoader("study")

    with pytest.raises(AttributeError):
        csvdl.save_to_file("fake_df_name")


def test_save_to_file_invalid_file_path(mocker: MockerFixture) -> None:
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    with pytest.raises(NotADirectoryError):
        csvdl.save_to_file("field_mapping", Path("fake_dir"))


def test_save_to_file_system_error(mocker: MockerFixture) -> None:
    csvdl = CsvDataLoader("study")
    csvdl._load_data.cache_clear()
    mocker.patch("pandas.DataFrame.to_csv", side_effect=ValueError)

    with pytest.raises(RuntimeError):
        csvdl.save_to_file("field_mapping")
