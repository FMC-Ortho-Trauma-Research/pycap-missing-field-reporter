from pathlib import Path

import pandas as pd
import pytest
from pytest_mock import MockerFixture
from redcap.project import Project

from dqm.config import DEFAULT_PYCAP_EXPORT_KWARGS, REDCAP_EXPORT_CONFIG
from dqm.data_loader.redcap_data_loader import RedcapDataLoader

DEFAULT_EXPORT_DIR = (
    Path(__file__).parent.parent.resolve() / "src" / "dqm" / "data" / "export"
)

TEST_DATA_DIR = Path(__file__).parent.resolve() / "test_data"

DF_NAMES = [
    "field_mapping",
    "field_metadata",
    "form_mapping",
    "project_data",
    "study_data",
]

FAKE_URL = "fake_url/api/"
FAKE_TOKEN = "32_char_api_token_0123456789ABCD"

DF_KWARGS = DEFAULT_PYCAP_EXPORT_KWARGS["df_kwargs"]


@pytest.fixture
def rcdl() -> RedcapDataLoader:
    rcdl = RedcapDataLoader("study", FAKE_URL, FAKE_TOKEN)
    rcdl._load_data.cache_clear()
    return rcdl


def get_pycap_method(df_name: str) -> str:
    method = REDCAP_EXPORT_CONFIG[df_name]["export_method"]
    assert isinstance(method, str)
    return method


def test_init_success(rcdl: RedcapDataLoader) -> None:
    rcdl_obj = rcdl

    assert rcdl_obj.study_name == "study"
    assert isinstance(rcdl_obj._project, Project)
    assert rcdl_obj.export_dir == DEFAULT_EXPORT_DIR


def test_init_custom_dir_success(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=True)

    rcdl = RedcapDataLoader(
        "study",
        FAKE_URL,
        FAKE_TOKEN,
        export_dir=Path("data"),
    )

    assert rcdl.study_name == "study"
    assert isinstance(rcdl._project, Project)
    assert rcdl.export_dir == Path("data")


def test_init_default_dir_not_exist(
mocker: MockerFixture,
) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")

    rcdl_obj = RedcapDataLoader(
        "study",
        FAKE_URL,
        FAKE_TOKEN,
    )

    assert rcdl_obj.export_dir == DEFAULT_EXPORT_DIR
    mock_mkdir.assert_called_once_with(parents=True)


@pytest.mark.parametrize(
    ("params"),
    [
        ([object(), FAKE_URL, FAKE_TOKEN, DEFAULT_EXPORT_DIR],),
        (["study", object(), FAKE_TOKEN, DEFAULT_EXPORT_DIR],),
        (["study", FAKE_URL, object(), DEFAULT_EXPORT_DIR],),
        (["study", FAKE_URL, FAKE_TOKEN, object()],),
    ],
)
def test_init_invalid_param_type(params: list[str | object | Path]) -> None:
    with pytest.raises(TypeError):
        RedcapDataLoader(*params)  # type: ignore[reportArgumentType]


def test_init_invalid_dir_path(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    with pytest.raises(NotADirectoryError):
        RedcapDataLoader(
            "study",
            FAKE_URL,
            FAKE_TOKEN,
            export_dir=Path("fake_dir"),
        )


def test_get_field_mapping_success(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method('field_mapping')}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "field_mapping.csv",
            **DF_KWARGS,
        ),
    )
    dff = rcdl.field_mapping

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


def test_get_field_metadata_success(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method('field_metadata')}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "field_metadata.csv",
            **DF_KWARGS,
        ),
    )
    dff = rcdl.field_metadata

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


def test_get_form_mapping_success(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method('form_mapping')}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "form_mapping.csv",
            **DF_KWARGS,
        ),
    )
    dff = rcdl.form_mapping

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()
    assert dff.eq("").sum().sum() == 0
    assert dff.columns.tolist() == [
        "arm_num",
        "unique_event_name",
        "form",
    ]


def test_get_project_data_success(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method('project_data')}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "project_data.csv",
            **DF_KWARGS,
        ),
    )
    dff = rcdl.project_data

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


def test_get_study_data_success(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method('study_data')}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / "study_data.csv",
            **DF_KWARGS,
        ),
    )
    dff = rcdl.study_data

    assert isinstance(dff, pd.DataFrame)
    assert not dff.empty
    assert (dff.dtypes == "object").all()


def test_get_data_single_api_call(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    rcdl_obj = rcdl

    for attr, config in REDCAP_EXPORT_CONFIG.items():
        assert isinstance(config["export_kwargs"], dict)
        mock_pycap_method = mocker.patch(
            f"redcap.project.Project.{get_pycap_method(attr)}",
            return_value=pd.read_csv(
                TEST_DATA_DIR / f"{attr}.csv",
                **DF_KWARGS,
            ),
        )

        getattr(rcdl_obj, attr)
        getattr(rcdl_obj, attr)
        getattr(rcdl_obj, attr)

        assert getattr(rcdl_obj, attr) is not None
        assert mock_pycap_method.call_count == 1


def test_get_data_pycap_error(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "redcap.project.Project.export_metadata",
        side_effect=Exception,
    )

    with pytest.raises(RuntimeError):
        rcdl.field_metadata


@pytest.mark.parametrize(
    "df_name",
    list(DF_NAMES),
)
def test_save_to_file_success_default_dir(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
    df_name: str,
) -> None:
    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv", return_value=None)
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method(df_name)}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / f"{df_name}.csv",
            **DF_KWARGS,
        ),
    )

    rcdl_obj = rcdl
    getattr(rcdl_obj, df_name)
    rcdl_obj.save_to_file(df_name)

    expected_file_path = DEFAULT_EXPORT_DIR / f"{df_name}.csv"
    mock_to_csv.assert_called_once_with(expected_file_path, index=False)


@pytest.mark.parametrize(
    "df_name",
    list(DF_NAMES),
)
def test_save_to_file_success_custom_dir(
    mocker: MockerFixture,
    df_name: str,
) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv", return_value=None)
    mocker.patch(
        f"redcap.project.Project.{get_pycap_method(df_name)}",
        return_value=pd.read_csv(
            TEST_DATA_DIR / f"{df_name}.csv",
            **DF_KWARGS,
        ),
    )

    rcdl_obj = RedcapDataLoader(
        "study",
        FAKE_URL,
        FAKE_TOKEN,
        export_dir=Path("fake_dir"),
    )
    getattr(rcdl_obj, df_name)
    rcdl_obj.save_to_file(df_name)

    expected_file_path = Path("fake_dir") / f"{df_name}.csv"
    mock_to_csv.assert_called_once_with(expected_file_path, index=False)


def test_save_to_file_invalid_df_name(rcdl: RedcapDataLoader) -> None:
    err_str = "Invalid DataFrame name:"
    with pytest.raises(ValueError, match=err_str):
        rcdl.save_to_file("fake_df_name")


def test_save_to_file_invalid_file_path(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    with pytest.raises(NotADirectoryError):
        rcdl.save_to_file("study_data", Path("fake_dir"))


def test_save_to_file_system_error(
    rcdl: RedcapDataLoader,
    mocker: MockerFixture,
) -> None:
    mocker.patch("pandas.DataFrame.to_csv", side_effect=ValueError)

    with pytest.raises(RuntimeError):
        rcdl.save_to_file("study_data")
