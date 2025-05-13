# ✅ Test automatici – Backend Django (AdriaProject – Geoportale Adriaclim)

Questo progetto include una suite di test automatici per garantire la stabilità delle funzionalità critiche del backend.

## 📦 Dove si trovano i test

I test sono collocati nella cartella `tests/` all'interno del progetto Django:

AdriaProject/
├── manage.py
├── tests/
│ ├── test_dataset_manager.py # Test sulle funzioni di importazione/processing
│ ├── test_models.py # Test sul modello Node
│ ├── test_views.py # Test su API getAllNodes e getMetadataNew


## ▶️ Come eseguire i test

### ✅ Requisiti
- Il progetto deve essere avviato correttamente in Docker
- Il container `adriapp_django` deve essere attivo
- Il database PostGIS deve essere disponibile

### 🔁 1. Accedere al container Django

docker exec -it adriapp_django bash
📂 2. Spostarsi nella cartella del progetto Django
    cd /code/AdriaProject
🧪 3. Eseguire tutti i test
        python manage.py test
🧪 4. Eseguire test di un file specifico
        python manage.py test tests.test_dataset_manager
        python manage.py test tests.test_views
        python manage.py test tests.test_models
        python manage.py test tests.test_performance
🧠 Cosa verificano i test
        test_dataset_manager.py	-> Funzioni critiche di importazione e parsing dei dataset (getAllDatasets, process_dataset_row)
        test_views.py -> Risposte corrette da API chiave (getAllNodes, getMetadataNew)
        test_models.py -> Creazione e integrità del modello Node
        test_performance.py -> Misura dei tempi di risposta del backend isolando le chiamate a servizi esterni (getMetadataNew)
💡 Note aggiuntive
        Alcuni test usano mocking manuale per isolare il codice da dipendenze esterne (es. chiamate a URL o parsing file remoti).

        I test non modificano dati reali: utilizzano un database temporaneo Django.

        Il test getMetadataNew utilizza una versione simulata di getMetadata() per garantire affidabilità anche senza connessione.

📬 Supporto
        Per problemi nell'esecuzione dei test, assicurarsi che:
            Il container adriapp_django sia attivo (docker ps)
            Il database PostGIS sia accessibile dal container
            I percorsi siano corretti (/code/AdriaProject è la root Django)