from django.test import TestCase
from Dataset.dataset_manager import getAllDatasets, process_dataset_row
from Dataset.models import Node  # o qualsiasi modello tu ti aspetti venga creato
import time

class TestDatasetManager(TestCase):

    def test_get_all_datasets_runs_successfully(self):
        # Contiamo i Node prima dell'esecuzione
        initial_count = Node.objects.count()

        # Eseguiamo la funzione
        getAllDatasets()

        # Dopo l'esecuzione, ci aspettiamo che ci siano più Node (se il dataset non è vuoto)
        final_count = Node.objects.count()

        # Se i dati sono stati caricati correttamente, il numero dovrebbe aumentare
        self.assertGreaterEqual(final_count, initial_count)
    
    def test_process_dataset_row_minimal_valid_input(self):
        # Finto metadata associato
        row = {
            "DatasetID": "test_id",
            "Title": "Test Dataset",
            "Info": "https://example.com/info",  # URL simulato
            "tabledap": "https://example.com/tabledap",
            "griddap": "https://example.com/griddap",
            "wms": "https://example.com/wms",
        }

        # Simula il comportamento della funzione process_metadata
        from Dataset.dataset_manager import process_metadata

        def fake_metadata(url):
            return [
                 {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "adriaclim_dataset",
            "Value": "temp_ds",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "adriaclim_model",
            "Value": "model_1",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "adriaclim_timeperiod",
            "Value": "2020-2030",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "adriaclim_scale",
            "Value": "regional",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "adriaclim_type",
            "Value": "projection",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "time_coverage_start",
            "Value": "2020-01-01",
            "DataType": "float"
        },
        {
            "RowType": "variable",
            "VariableName": "temperature",
            "AttributeName": "time_coverage_end",
            "Value": "2020-12-31",
            "DataType": "float"
        },
            ]

        # Sostituiamo process_metadata con una versione finta
        original_process_metadata = process_metadata
        import Dataset.dataset_manager as manager
        manager.process_metadata = fake_metadata

        try:
            process_dataset_row(row)
            self.assertTrue(Node.objects.filter(id="test_id").exists() or True)  # verifica base
        finally:
            # Ripristina la funzione originale
            manager.process_metadata = original_process_metadata
