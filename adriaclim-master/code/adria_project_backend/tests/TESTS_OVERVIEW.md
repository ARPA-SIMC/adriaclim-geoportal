
# TESTS_OVERVIEW.md — AdriaClim Backend

## 🇮🇹 Descrizione Dettagliata dei Test (Italiano)

### tests/test_database_operations.py
- Verifica il controllo dello spazio su database.
- Test:
  - `test_is_database_almost_full_true`: Simula database quasi pieno (95%); deve segnalare True.
  - `test_is_database_almost_full_false`: Simula database al 70%; deve segnalare False.

### tests/test_dataset_manager.py
- Copertura di funzioni critiche di importazione e parsing dei dataset.
- Test:
  - `test_get_all_datasets_runs_successfully`: Verifica che l'importazione non generi errori e non cancelli dati.
  - `test_process_dataset_row_minimal_valid_input`: Testa l'importazione di una riga di dataset con dati minimi.
  - `test_process_metadata_success/failure`: Verifica il parsing dei metadata con CSV valido e con errore.
  - `test_fetch_datasets_success/failure`: Verifica il caricamento dataset con CSV valido e con errore.
  - `test_node_found_returns_json` / `test_indicator_found_returns_json` / `test_no_node_or_indicator_returns_none`: Testano il recupero dei metadata associati a nodi o indicatori.

### tests/test_external_wms.py
- Test di funzioni ausiliarie per l'interazione con servizi WMS.
- Test:
  - `test_build_wms_url_removes_none_values`: Verifica la corretta generazione dell'URL WMS senza parametri None.
  - `test_fetch_wms_response_success/error`: Verifica il comportamento corretto in caso di risposta valida o errore di rete.

### tests/test_models.py
- Test sui modelli Django.
- Test:
  - `test_node_creation`: Verifica la corretta creazione e salvataggio del modello Node.

### tests/test_performance.py
- Test di performance.
- Test:
  - `test_metadata_response_time`: Misura il tempo di risposta della view `getMetadataNew` con mock.

### tests/test_urls.py
- Test di routing.
- Test:
  - `test_all_nodes` / `test_get_metadata_table`: Verificano che le URL corrispondano correttamente alle view attese.

### tests/test_views.py
- Test sulle API e sulle view principali.
- Test:
  - `test_get_all_nodes`: Verifica la risposta corretta della view `getAllNodes`.
  - `test_get_metadata_new`: Verifica la view `getMetadataNew` con mock.
  - `test_get_overlays`: Verifica la view `get_overlays_new` con mock WMS.

---

## 🇬🇧 Detailed Test Description (English)

### tests/test_database_operations.py
- Verifies database space monitoring.
- Tests:
  - `test_is_database_almost_full_true`: Simulates near-full DB (95%); must return True.
  - `test_is_database_almost_full_false`: Simulates 70% DB usage; must return False.

### tests/test_dataset_manager.py
- Covers critical dataset import and parsing functions.
- Tests:
  - `test_get_all_datasets_runs_successfully`: Checks that dataset import does not raise errors or delete data.
  - `test_process_dataset_row_minimal_valid_input`: Tests importing a minimal dataset row.
  - `test_process_metadata_success/failure`: Tests metadata parsing with valid CSV and error cases.
  - `test_fetch_datasets_success/failure`: Tests dataset loading with valid CSV and error cases.
  - `test_node_found_returns_json` / `test_indicator_found_returns_json` / `test_no_node_or_indicator_returns_none`: Test fetching metadata linked to nodes or indicators.

### tests/test_external_wms.py
- Tests for WMS-related utility functions.
- Tests:
  - `test_build_wms_url_removes_none_values`: Ensures correct WMS URL generation excluding None parameters.
  - `test_fetch_wms_response_success/error`: Verifies correct behavior on valid response or network error.

### tests/test_models.py
- Tests on Django models.
- Test:
  - `test_node_creation`: Verifies correct creation and saving of the Node model.

### tests/test_performance.py
- Performance tests.
- Test:
  - `test_metadata_response_time`: Measures response time of `getMetadataNew` view with mock.

### tests/test_urls.py
- URL routing tests.
- Tests:
  - `test_all_nodes` / `test_get_metadata_table`: Verify URL patterns correctly map to expected views.

### tests/test_views.py
- API and view tests.
- Tests:
  - `test_get_all_nodes`: Verifies correct response of `getAllNodes` view.
  - `test_get_metadata_new`: Verifies `getMetadataNew` view with mock.
  - `test_get_overlays`: Verifies `get_overlays_new` view with WMS mock.

---

