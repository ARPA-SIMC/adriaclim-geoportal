
# AdriaClim Backend — Test Suite Documentation

--- ITA

## Percorso del repository

```
adriaclim-master/code/adria_project_backend/tests
```
Questa è la directory ufficiale dei test per il backend, con una struttura organizzata per facilitare la manutenzione e l'espansione dei test.

## Esecuzione dei test

L'esecuzione dei test avviene interamente in ambiente Docker.

### Identificazione del container corretto

Il container Docker che esegue il backend Django si chiama:
```
django
```
Se in futuro il nome del servizio dovesse cambiare, è necessario aggiornare i comandi qui sotto sostituendo `django` con il nuovo nome.

### Avvio dei container

Prima di eseguire i test, assicurati che i container siano avviati. Dalla root del progetto, esegui:
```bash
docker compose up -d
```
Puoi controllare lo stato dei container con:
```bash
docker compose ps
```

### Esecuzione completa della suite di test

Dalla root del progetto, esegui il seguente comando per eseguire tutti i test:
```bash
docker compose exec django python adria_project_backend/manage.py test tests
```
Questo comando:
- Esegue tutti i test presenti nella directory `tests`.
- Utilizza il container `django` definito nel file `docker-compose.yml`.
- Garantisce un ambiente isolato e controllato.

### Esecuzione di un singolo file di test

Per eseguire un singolo file di test specifico all'interno della directory `tests`:
```bash
docker compose exec django python adria_project_backend/manage.py test tests.test_nome_file
```
Sostituisci `test_nome_file` con il nome effettivo del file (senza l'estensione `.py`).

Esempio:
```bash
docker compose exec django python adria_project_backend/manage.py test tests.test_database_operations
```
Questa opzione è utile per testare solo una specifica funzionalità o durante il debug.

## Considerazioni tecniche

- Tutti i test utilizzano il framework integrato di Django (`django.test.TestCase`) e fanno ampio uso di `unittest.mock` per isolare le dipendenze esterne.
- I dati creati durante l'esecuzione vengono automaticamente isolati e rimossi al termine del test.
- Attenzione: i log potrebbero riportare messaggi di "errore" simulati nei test, ma questi sono normali e fanno parte dei casi di test.
- Assicurati che il database di test sia correttamente configurato nei container Docker.

## Struttura e organizzazione dei test

I test sono suddivisi in categorie funzionali:
- Test delle API e delle view
- Test dei modelli Django
- Test di performance
- Test delle utility interne
- Test del routing e URL mapping

Ogni modulo di test include commenti tecnici chiari e mirati per facilitare la lettura e la manutenzione.

## Supporto e riferimenti

Per problematiche relative ai test o alla configurazione Docker, consulta la documentazione tecnica interna oppure contatta il team di sviluppo backend di AdriaClim.


--- ENG

# AdriaClim Backend — Test Suite Documentation (English Version)

## Repository Path

```
adriaclim-master/code/adria_project_backend/tests
```
This is the official directory containing the automated test suite for the AdriaClim backend, organized for easy maintenance and future test expansions.

## Running the Tests

All tests are executed entirely within the Docker environment.

### Identifying the Correct Container

The Docker container running the Django backend is named:
```
django
```
If the service name changes in the future, replace `django` in the commands below with the new name.

### Starting the Containers

Before running the tests, make sure the containers are running. From the project root, execute:
```bash
docker compose up -d
```
Check the container status with:
```bash
docker compose ps
```

### Full Test Suite Execution

From the project root, execute the following command to run all tests:
```bash
docker compose exec django python adria_project_backend/manage.py test tests
```
This command:
- Runs all tests inside the `tests` directory.
- Uses the `django` container defined in the `docker-compose.yml` file.
- Ensures a controlled and isolated environment.

### Running a Specific Test File

To run a specific test file inside the `tests` directory:
```bash
docker compose exec django python adria_project_backend/manage.py test tests.test_file_name
```
Replace `test_file_name` with the actual filename (without the `.py` extension).

Example:
```bash
docker compose exec django python adria_project_backend/manage.py test tests.test_database_operations
```
This option is useful for debugging or testing a specific functionality.

## Technical Considerations

- All tests use Django's built-in testing framework (`django.test.TestCase`) and extensively utilize `unittest.mock` to isolate external dependencies.
- Data created during test execution is automatically isolated and removed after tests finish.
- Note: Logs may display simulated “error” messages during tests; these are expected as part of the test cases.
- Ensure the test database is correctly configured in the Docker containers.

## Test Structure and Organization

Tests are grouped into functional categories:
- API and View Tests
- Django Model Tests
- Performance Tests
- Internal Utility Tests
- Routing and URL Mapping Tests

Each test module includes clear, technical comments to ease understanding and maintenance.

## Support and References

For issues related to tests or Docker configuration, refer to the internal technical documentation or contact the AdriaClim backend development team.
