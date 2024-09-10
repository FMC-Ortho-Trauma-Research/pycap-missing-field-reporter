from pathlib import Path

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from dqm.data_loader.csv_data_loader import CSVDataLoader


class TestCSVDataLoader:
    TEST_DATA_DIR = Path(__file__).parent.resolve() / "data"
    DEFAULT_SOURCE_DIR = (
        Path(__file__).parent.parent.resolve() / "src" / "dqm" / "data" / "raw"
    )

    def test_init_default_dir(self) -> None:
        name = "study_name"

        csvdl = CSVDataLoader(name)

        assert isinstance(csvdl, CSVDataLoader)
        assert csvdl.study_name == "study_name"
        assert isinstance(csvdl.source_dir, Path)
        assert csvdl.source_dir == self.DEFAULT_SOURCE_DIR

    def test_init_custom_dir(self, mocker: MockerFixture) -> None:
        name = "study_name"
        custom_dir = "/home/exampleuser/data"
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.is_dir", return_value=True)

        csvdl = CSVDataLoader(name, custom_dir)

        assert isinstance(csvdl, CSVDataLoader)
        assert csvdl.study_name == "study_name"
        assert isinstance(csvdl.source_dir, Path)
        assert csvdl.source_dir == Path("/home/exampleuser/data")

    def test_init_invalid_name(self) -> None:
        int_name = 123
        custom_name = object()

        with pytest.raises(TypeError):
            CSVDataLoader(int_name)  # type: ignore[reportArgumentType]
        with pytest.raises(TypeError):
            CSVDataLoader(custom_name)  # type: ignore[reportArgumentType]

    def test_init_invalid_path_file(self, mocker: MockerFixture) -> None:
        name = "study_name"
        path_to_file = "/home/exampleuser/data.csv"
        mocker.patch("pathlib.Path.exists", return_value=True)

        with pytest.raises(NotADirectoryError):
            CSVDataLoader(name, path_to_file)

    def test_init_invalid_path_dir(self, mocker: MockerFixture) -> None:
        name = "study_name"
        path_to_dir = "/home/exampleuser/data"
        mocker.patch("pathlib.Path.exists", return_value=False)

        with pytest.raises(FileNotFoundError):
            CSVDataLoader(name, path_to_dir)

    def test_get_dataframes_single(self) -> None:
        dataframes = ("metadata",)
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)

        df_dict = csvdl.get_dataframes(dataframes)

        assert isinstance(df_dict, dict)
        assert len(df_dict) == 1
        assert isinstance(df_dict["metadata"], pd.DataFrame)
        assert not df_dict["metadata"].empty

    def test_get_dataframes_multiple(self) -> None:
        dataframes = ("field_names", "metadata", "study_data")
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)

        df_dict = csvdl.get_dataframes(dataframes)

        assert isinstance(df_dict, dict)
        assert len(df_dict) == 3
        for name in dataframes:
            assert isinstance(df_dict[name], pd.DataFrame)
            assert not df_dict[name].empty

    def test_get_dataframes_invalid_param(self) -> None:
        invalid_param_type = "metadata"
        invalid_name_type = ("metadata", 123)
        invalid_name_key = ("metadata", "fields")
        err_str = "Value: 'fields' is not a valid dataframe name!"
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)

        with pytest.raises(TypeError):
            csvdl.get_dataframes(invalid_param_type)  # type: ignore[reportArgumentType]
        with pytest.raises(TypeError):
            csvdl.get_dataframes(invalid_name_type)  # type: ignore[reportArgumentType]
        with pytest.raises(ValueError, match=err_str):
            csvdl.get_dataframes(invalid_name_key)

    def test_get_dataframes_missing_source_file(
        self,
        mocker: MockerFixture,
    ) -> None:
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)
        dataframes = ("metadata",)
        mocker.patch("pathlib.Path.exists", return_value=False)

        with pytest.raises(FileNotFoundError):
            csvdl.get_dataframes(dataframes)

    def test_get_dataframes_invalid_source_file(
        self,
        mocker: MockerFixture,
    ) -> None:
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)
        dataframes = ("metadata",)
        mocker.patch("pandas.read_csv", side_effect=pd.errors.ParserError)

        with pytest.raises(pd.errors.ParserError):
            csvdl.get_dataframes(dataframes)

    def test_get_dataframes_dtypes(self) -> None:
        csvdl = CSVDataLoader("study_name", self.TEST_DATA_DIR)
        dataframes = ("study_data",)
        df_dict = csvdl.get_dataframes(dataframes)

        assert isinstance(df_dict["study_data"], pd.DataFrame)
        assert (df_dict["study_data"].dtypes == "object").all()
