import pandas as pd
import pytest
from pytest_mock import MockerFixture
from redcap.project import Project

from dqm.data_loader.redcap_data_loader import REDCapDataLoader


class TestREDCapDataLoader:
    def test_init_success(self) -> None:
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        assert isinstance(rcdl, REDCapDataLoader)
        assert rcdl.study_name == "study_name"
        assert isinstance(rcdl.project, Project)
        assert isinstance(rcdl._dataframes, dict)
        assert rcdl._dataframes == {}

    @pytest.mark.parametrize(
        ("study_name", "url", "token"),
        [
            (123, "api_url/api/", "32char_api_token_123456789ABCDEF"),
            ("study_name", 123, "32char_api_token_123456789ABCDEF"),
            ("study_name", "api_url/api/", 123),
        ],
    )
    def test_init_illegal_param_type(self, study_name, url, token) -> None:
        with pytest.raises(TypeError):
            REDCapDataLoader(study_name, url, token)

    @pytest.mark.parametrize(
        ("study_name", "url", "token"),
        [
            ("study_name", "garbage_str", "32char_api_token_123456789ABCDEF"),
            ("study_name", "api_url/api/", "garbage_token"),
            ("study_name", "", ""),
        ],
    )
    def test_init_handle_pycap_exception(self, study_name, url, token) -> None:
        err_str = "Error while initializing Pycap `Project` object!"
        with pytest.raises(ValueError, match=err_str):
            REDCapDataLoader(study_name, url, token)

    def test_get_dataframes_single(self, mocker) -> None:
        mocker.patch(
            "redcap.project.Project.export_metadata",
            return_value=pd.DataFrame(),
        )
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        df_dict = rcdl.get_dataframes(("metadata",))

        assert len(rcdl._dataframes) == 1
        assert isinstance(df_dict, dict)
        assert isinstance(rcdl._dataframes["metadata"], pd.DataFrame)
        assert isinstance(df_dict["metadata"], pd.DataFrame)

    def test_get_dataframes_multiple(self, mocker) -> None:
        mocker.patch(
            "redcap.project.Project.export_records",
            return_value=pd.DataFrame(),
        )
        mocker.patch(
            "redcap.project.Project.export_metadata",
            return_value=pd.DataFrame(),
        )
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        df_dict = rcdl.get_dataframes(("metadata", "study_data"))

        assert len(rcdl._dataframes) == 2
        assert isinstance(df_dict, dict)
        assert isinstance(rcdl._dataframes["metadata"], pd.DataFrame)
        assert isinstance(df_dict["metadata"], pd.DataFrame)
        assert isinstance(rcdl._dataframes["study_data"], pd.DataFrame)
        assert isinstance(df_dict["study_data"], pd.DataFrame)

    @pytest.mark.parametrize(
        "dataframes",
        [
            123,
            ("metadata", 123),
            ("metadata", "study_data", 123),
        ],
    )
    def test_get_dataframes_invalid_param_type(self, dataframes) -> None:
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        with pytest.raises(TypeError):
            rcdl.get_dataframes(dataframes)

    def test_get_dataframes_invalid_param_value(self) -> None:
        err_str = "Value: 'fields' is not a valid dataframe name!"
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        with pytest.raises(ValueError, match=err_str):
            rcdl.get_dataframes(("metadata", "fields"))

    def test_get_dataframes_handle_pycap_exception(self, mocker) -> None:
        mocker.patch(
            "redcap.project.Project.export_metadata",
            side_effect=Exception,
        )
        mocker.patch(
            "redcap.project.Project.export_records",
            side_effect=Exception,
        )
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        with pytest.raises(SystemError):
            rcdl.get_dataframes(("metadata", "study_data"))

    def test_get_dataframes_illegal_dtypes(self, mocker) -> None:
        mocker.patch(
            "redcap.project.Project.export_records",
            return_value= pd.DataFrame(
                {
                    "field1": [1, 2, 3],
                    "field2": ["a", "b", "c"],
                    "field3": [1.1, 2.2, 3.3],
                    "field4": [True, False, True],
                },
            ),
        )
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        with pytest.raises(TypeError):
            rcdl.get_dataframes(("study_data",))

    def test_get_dataframes_dtypes_success(self, mocker) -> None:
        mocker.patch(
            "redcap.project.Project.export_records",
            return_value= pd.DataFrame(
                {
                    "field1": ["1", "2", "3"],
                    "field2": ["a", "b", "c"],
                    "field3": ["1.1", "2.2", "3.3"],
                    "field4": ["True", "False", "True"],
                },
            ),
        )
        rcdl = REDCapDataLoader(
            "study_name",
            "api_url/api/",
            "32char_api_token_123456789ABCDEF",
        )

        df_dict = rcdl.get_dataframes(("study_data",))

        assert isinstance(df_dict["study_data"], pd.DataFrame)
        assert (df_dict["study_data"].dtypes == "object").all()
