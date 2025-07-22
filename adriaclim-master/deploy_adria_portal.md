## 1

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

## 2

# Deploy del Geoportale AdriaClim tramite Jenkins

Questa guida illustra in dettaglio la procedura per installare, configurare e mettere online il Geoportale AdriaClim tramite Jenkins su un server Rocky Linux (o compatibile), partendo dal repository Git.  
Tutti i passaggi sono pensati per essere ripetibili dai tecnici Arpae, garantendo sicurezza, tracciabilità e automazione del processo di deploy.

---

## Requisiti

- **Server** Rocky Linux 8.x (o CentOS/RHEL 8.x compatibile)
- **Accesso SSH** al server con permessi sudo/root
- **Docker** e **Docker Compose** installati e funzionanti (`docker --version`, `docker compose version`)
- **Jenkins** installato e raggiungibile (es: http://<IP-SERVER>:8080)
- **Account utente Jenkins** per l’accesso alla dashboard
- **Credenziali di servizio già configurate** su Jenkins (PAT GitHub, file segreto .env)
- **Accesso al repository GitHub** del progetto

---

## 1. Installazione prerequisiti (da eseguire una sola volta)

Se la VM non è già pronta, installare:

- **Docker**
- **Java** (per Jenkins)
- **Jenkins**
- **Permessi utente Jenkins**
    - L’utente Jenkins deve essere nel gruppo `docker` e avere la shell `/bin/bash`.
- *(Opzionale)* **Aprire porte firewall** per Jenkins (8080) e il portale (8000).

---

## 2. Accesso e configurazione Jenkins

- Collegarsi via browser a:  
  `http://<IP-DEL-SERVER>:8080`
- Completare la configurazione iniziale  
  *(la password iniziale si trova con: `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`)*
- Installare i plugin suggeriti
- Creare gli utenti amministrativi necessari

> **Nota:** Questi passaggi vanno fatti una sola volta dopo l’installazione

---

## 3. Configurazione delle credenziali Jenkins

- **PAT GitHub:**  
  Inserire tra le credenziali Jenkins  
  (`Gestione credenziali > System > Aggiungi credenziale > Username/Password`)
- **File segreto .env:**  
  Caricare il file `.env` necessario come “File segreto”, annotando il nome usato nella pipeline

---

## 4. Creazione pipeline multibranch

- Dal menu Jenkins:  
  `Nuovo Item` > `Pipeline multibranch`
- Inserire il nome del progetto (es: `AdriaClimPlus`)
- Selezionare come “source” il repository GitHub
- Scegliere la credenziale GitHub appena configurata
- Salvare e lasciare che Jenkins effettui la scansione dei branch  
  *(verificare che venga rilevato il Jenkinsfile)*

---

## 5. Pipeline automatica: flusso di deploy

La pipeline esegue **automaticamente** i seguenti step per ogni branch che contiene un Jenkinsfile valido:

1. **Checkout** del repository (clone del branch)
2. **Iniezione** del file `.env` tramite credenziale segreta Jenkins
3. **Pulizia ambiente e container**  
   (`docker compose down` e `docker system prune`)
4. **Build e avvio dei container**  
   `docker compose up -d --build`
5. **Verifica stato container**  
   `docker compose ps`
6. **Esecuzione test automatici** (se previsti nel Jenkinsfile)
7. **Log risultati e stato deploy**

---

## 6. Verifica manuale post-deploy

- Visitare il portale su:  
  `http://<IP-DEL-SERVER>:8000/`
- Controllare eventuali errori nei log:  
  `docker compose logs -f`

---

## 7. Aggiornamento codice e ripetizione deploy

- Ogni **push su GitHub** (su branch monitorati) scatena in automatico una nuova build della pipeline
- In alternativa, la pipeline può essere avviata **manualmente** dalla dashboard Jenkins

---

## 8. Gestione credenziali e manutenzione

- I tecnici devono solo accedere a Jenkins con il proprio account  
  *(le credenziali di servizio sono già impostate e non vanno ricreate)*
- Per **aggiornare la credenziale GitHub** (es: nuovo PAT):
    1. Vai su “Gestione credenziali”, aggiungi il nuovo PAT
    2. Sostituiscilo nelle pipeline come “source”
    3. Elimina la vecchia credenziale se non serve più

---

## 9. Troubleshooting

- **Permessi Docker negati:**  
  Assicurarsi che l’utente Jenkins sia nel gruppo `docker` e che la shell sia `/bin/bash`
- **Copia file .env fallita:**  
  Verificare permessi del workspace e corretta configurazione della credenziale “file segreto”
- **Pipeline non trova Jenkinsfile:**  
  Verificare posizione/nome branch e che il file sia presente nel repository
- **Il sito non si apre:**  
  Controllare che la porta sia esposta, container siano “Up”, firewall non blocchi

---

## 10. Note di sicurezza

- Utilizzare solo account GitHub tecnici o aziendali dedicati
- Ruotare periodicamente PAT/token di accesso
- Mantenere Jenkins, Docker e plugin aggiornati
- Proteggere l’accesso alla VM e a Jenkins con password robuste

---

## 11. Accesso dei tecnici ARPAE

- Le pipeline, credenziali e segreti sono già configurati dal responsabile del setup.
- I tecnici devono richiedere solo:
    - Utente VM (per SSH/terminali, se serve)
    - Utente Jenkins (per dashboard web e pipeline)
- Tutto il resto (PAT, file .env, setup pipeline) è già predisposto, salvo cambio policy.

---

## Supporto

Per problemi o dubbi, contattare il team tecnico o aprire una issue nel repository.

