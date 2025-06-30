# Obiettivo
Questa guida descrive i passaggi necessari per installare e avviare il Geoportale AdriaClim su un server virtuale, a partire dal repository Git. Le istruzioni sono pensate per essere eseguite da tecnici Arpae in ambiente Linux, utilizzando Docker e Docker Compose.

# Requisiti
    - Sistema operativo Linux
    - Accesso SSH al server virtuale
    - Docker e Docker Compose installati
    - Accesso al repository Git del progetto

# Procedura di deploy
    1. Clonare il repository
        git clone https://<URL-del-repository>/adria-project.git
        cd adriaclim-master
    2. Creare i file `.env`
        I file `.env` contengono variabili d’ambiente sensibili. Non sono inclusi nel repository e devono essere creati manualmente.
            File 1 — adriaclim-master/.env:
                POSTGRES_NAME=
                POSTGRES_USER=
                POSTGRES_PASSWORD=
            File 2 — code/adria_project_backend/.env con contenuto:
                SECRET_KEY='inserire-la-secret-key-django-qui'
    3. Avviare il progetto con Docker
        docker compose up --build

# Note importanti
Line Ending (CRLF vs LF)
Assicurarsi che tutti gli script (.sh, inclusi entrypoint.sh) abbiano fine riga in formato UNIX (LF). Se sono in formato Windows (CRLF), Docker potrebbe restituire l’errore:
    exec /entrypoint.sh: exec format error
Per correggere:
    • Con editor come VS Code: impostare LF in basso a destra
    • Oppure da terminale:
        dos2unix entrypoint.sh

# Verifica finale
    • Visitare il portale all’indirizzo http://<IP-del-server>:8000/
    • Controllare che non ci siano errori nei log:
            docker compose logs -f

# Manutenzione base
    Per aggiornare il codice e riavviare:
        git pull
        docker compose up --build
    Per arrestare tutto:
        docker compose down
    Gestione sicura dei `.env`
        I file `.env` non devono essere inclusi nel repository. Vanno copiati manualmente sul server via SCP o SSH prima dell’avvio dei container.
Esempio:
    scp code/adria_project_backend/.env utente@server:/percorso/progetto/code/adria_project_backend/.env
Supporto:
    Per problemi o dubbi, contattare il team tecnico o aprire un issue nel repository.
