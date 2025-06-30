from django.test import TestCase
from unittest.mock import patch, MagicMock
import pandas as pd
from Dataset.dataset_manager import getAllDatasets, process_dataset_row, process_metadata, getMetadataOfASpecificDataset, fetch_datasets
from Dataset.models import Node, Indicator
from io import StringIO

class TestDatasetManager(TestCase):

    def test_get_all_datasets_runs_successfully(self):
        initial_count = Node.objects.count()
        getAllDatasets()
        final_count = Node.objects.count()
        self.assertGreaterEqual(final_count, initial_count)

    @patch("Dataset.dataset_manager.process_metadata")
    def test_process_dataset_row_minimal_valid_input(self, mock_process_metadata):
        mock_process_metadata.return_value = [
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "adriaclim_dataset", "Value": "test_ds", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "adriaclim_model", "Value": "model_1", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "adriaclim_timeperiod", "Value": "2020-2030", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "adriaclim_scale", "Value": "regional", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "adriaclim_type", "Value": "projection", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "time_coverage_start", "Value": "2020-01-01", "DataType": "float"},
            {"RowType": "variable", "VariableName": "temperature", "AttributeName": "time_coverage_end", "Value": "2020-12-31", "DataType": "float"},
        ]

        row = {
            "DatasetID": "test_id_123",
            "Title": "Test Dataset",
            "Info": "https://example.com/info",
            "tabledap": "https://example.com/tabledap",
            "griddap": "https://example.com/griddap",
            "wms": "https://example.com/wms",
        }

        self.assertFalse(Node.objects.filter(id="test_id_123").exists())
        process_dataset_row(row)
        self.assertTrue(Node.objects.filter(id="test_id_123").exists())

INFO_COLUMNS = ["col1", "col2", "col3"]

class ProcessMetadataTests(TestCase):

    @patch("Dataset.dataset_manager.download_with_cache_as_csv")
    @patch("Dataset.dataset_manager.INFO_COLUMNS", INFO_COLUMNS)
    def test_process_metadata_success(self, mock_download):
        fake_csv = StringIO("header1,header2,header3\nval1,val2,val3\nval4,val5,val6\n")
        df = pd.read_csv(fake_csv, names=INFO_COLUMNS)
        df.iloc[0] = ["nan", "nan", "nan"]
        fake_csv.seek(0)

        mock_download.return_value = fake_csv

        with patch("pandas.read_table", return_value=df):
            result = process_metadata("http://fake-url.com/metadata.csv")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], {"col1": "val1", "col2": "val2", "col3": "val3"})

    @patch("Dataset.dataset_manager.download_with_cache_as_csv")
    def test_process_metadata_failure(self, mock_download):
        mock_download.side_effect = Exception("Fake error")
        result = process_metadata("http://fake-url.com/fail.csv")
        self.assertEqual(result, [])

class GetMetadataOfASpecificDatasetTests(TestCase):

    @patch("Dataset.dataset_manager.requests.get")
    def test_node_found_returns_json(self, mock_get):
        node = Node.objects.create(
            id="node1",
            title="Test Node",
            metadata_url="http://example.com/data.csv"
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"mock": "data"}
        mock_get.return_value = mock_response

        result = getMetadataOfASpecificDataset("node1")
        self.assertEqual(result, {"mock": "data"})

    @patch("Dataset.dataset_manager.requests.get")
    def test_indicator_found_returns_json(self, mock_get):
        indicator = Indicator.objects.create(
            dataset_id="ind1",
            title="Test Indicator",
            metadata_url="http://example.com/data.csv"
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"mock": "data"}
        mock_get.return_value = mock_response

        result = getMetadataOfASpecificDataset("ind1")
        self.assertEqual(result, {"mock": "data"})

    def test_no_node_or_indicator_returns_none(self):
        result = getMetadataOfASpecificDataset("nonexistent_id")
        self.assertIsNone(result)

DATASET_COLUMNS = ["col1", "col2", "col3"]

class FetchDatasetsTests(TestCase):

    @patch("Dataset.dataset_manager.download_with_cache_as_csv")
    @patch("Dataset.dataset_manager.DATASET_COLUMNS", DATASET_COLUMNS)
    def test_fetch_datasets_success(self, mock_download):
        fake_csv = StringIO("col1,col2,col3\nval1,val2,val3\nval4,val5,val6\n")
        df = pd.read_csv(fake_csv, names=DATASET_COLUMNS)
        fake_csv.seek(0)

        mock_download.return_value = fake_csv

        with patch("pandas.read_table", return_value=df):
            result = fetch_datasets()
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 2)
            self.assertEqual(result.iloc[0].to_dict(), {"col1": "val1", "col2": "val2", "col3": "val3"})

    @patch("Dataset.dataset_manager.download_with_cache_as_csv")
    def test_fetch_datasets_failure(self, mock_download):
        mock_download.side_effect = Exception("Fake download error")
        result = fetch_datasets()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
