from unittest import TestCase
from unittest.mock import patch
from myFunctions.database_operations import is_database_almost_full

class TestDatabaseOperations(TestCase):
    
    @patch("myFunctions.database_operations.connection")
    def test_is_database_almost_full_true(self, mock_connection):
        # Simulazione: il database ha raggiunto il 95% di utilizzo (104 MB su 110 MB).
        # Questo test verifica che la funzione rilevi correttamente una situazione di spazio quasi esaurito.
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = (104 * 1024 * 1024, "104 MB")

        result = is_database_almost_full(threshold_percentage=90)
        self.assertTrue(result)

    @patch("myFunctions.database_operations.connection")
    def test_is_database_almost_full_false(self, mock_connection):
        # Simulazione: il database è al 70% di utilizzo (77 MB su 110 MB).
        # Questo test verifica che la funzione NON segnali falsamente una situazione di emergenza.
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = (77 * 1024 * 1024, "77 MB")

        result = is_database_almost_full(threshold_percentage=90)
        self.assertFalse(result)

