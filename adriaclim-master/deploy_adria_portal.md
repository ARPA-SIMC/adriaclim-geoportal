# 🌍 Deploy del Geoportale AdriaClim tramite Jenkins

Questa guida illustra in dettaglio la procedura per installare, configurare e mettere online il Geoportale AdriaClim tramite Jenkins su un server Rocky Linux (o compatibile), partendo dal repository Git.  
È pensata per essere **ripetibile** e **manutenibile** dal team tecnico ARPAE, garantendo **automazione, sicurezza e tracciabilità**.

---

## Requisiti minimi

- Server **Rocky Linux 8.x** (o CentOS/RHEL compatibile)
- **Accesso SSH** con permessi `sudo`
- **Docker** e **Docker Compose** installati (`docker --version`)
- **Jenkins** installato e raggiungibile (`http://<IP>:8080`)
- Accesso al **repository GitHub** del progetto
- Account Jenkins con accesso alla dashboard
- Credenziali Jenkins già configurate:
  - PAT GitHub
  - File `.env` come “file segreto”
  - Chiave SSH (se richiesta)

---

# 1. Setup iniziale (da fare solo una volta)

### 1.1 Installare i prerequisiti (se mancanti)
```bash
sudo dnf install -y docker docker-compose java-11-openjdk
```

### 1.2 Aggiungere Jenkins al gruppo `docker`
```bash
sudo usermod -aG docker jenkins
sudo chsh -s /bin/bash jenkins
sudo systemctl restart jenkins
```

### 1.3 (Opzionale) Aprire le porte nel firewall
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp  # Jenkins
sudo firewall-cmd --permanent --add-port=8000/tcp  # Geoportale
sudo firewall-cmd --reload
```

### 1.4 Configurazione iniziale Jenkins (via browser)

- Accedi via browser: `http://<IP-DEL-SERVER>:8080`
- Inserisci la password iniziale:
  ```bash
  sudo cat /var/lib/jenkins/secrets/initialAdminPassword
  ```
- Installa i plugin suggeriti
- Crea gli utenti amministratori Jenkins

---

# 2. Configurazione delle credenziali Jenkins

- Vai su: `Gestione Jenkins > Gestione credenziali > System`
- Aggiungi le seguenti:
  - **PAT GitHub**: tipo “Username/Password”, con username GitHub e PAT come password
  - **File .env**: tipo “File segreto”, carica il file `.env` del progetto
  - **(Opzionale)** chiave SSH se il repo GitHub richiede autenticazione via SSH

---

# 3. Creazione della pipeline multibranch

- Vai su: `Nuovo Item > Pipeline multibranch`
- Inserisci un nome (es. `AdriaClimPlus`)
- Come sorgente, scegli GitHub e inserisci l’URL del repository
- Seleziona la credenziale GitHub configurata
- Salva: Jenkins effettuerà la scansione automatica dei branch
- Verifica che venga rilevato il `Jenkinsfile` nel branch corretto

---

# 4. Flusso automatico della pipeline

Ogni volta che viene eseguita (manualmente o da push su GitHub), la pipeline esegue in ordine:

1. **Checkout del repository**
2. **Iniezione del file `.env`** tramite credenziale segreta
3. **Pulizia ambiente**  
   ```bash
   docker compose down && docker system prune -f
   ```
4. **Build e avvio dei container**  
   ```bash
   docker compose up -d --build
   ```
5. **Verifica stato container**  
   ```bash
   docker compose ps
   ```
6. **Esecuzione test automatici** (se previsti nel `Jenkinsfile`)
7. **Log finale e stato del deploy**

---

# 👁️5. Verifica post-deploy

- Apri il portale su: `http://<IP-DEL-SERVER>:8000/`
- Verifica che sia online
- Controlla i log in tempo reale con:
  ```bash
  docker compose logs -f
  ```

---

# 6. Aggiornamento del codice e rilancio deploy

- Ogni **push su GitHub** (su branch monitorati) scatena **automaticamente** una nuova build
- In alternativa, puoi avviare la pipeline **manualmente** dalla dashboard Jenkins

---

# 7. Manutenzione e aggiornamento credenziali

- Per aggiornare un PAT GitHub:
  1. Vai su “Gestione credenziali”
  2. Aggiungi il nuovo PAT
  3. Aggiorna la pipeline per usare la nuova credenziale
  4. Elimina la vecchia (se non più usata)

---

# 8. Troubleshooting comuni

- **Permessi Docker negati:**  
  Assicurati che l’utente Jenkins sia nel gruppo `docker` e abbia la shell `/bin/bash`

- **Errore file .env:**  
  Verifica che sia stato caricato correttamente come “file segreto”

- **Pipeline non trova Jenkinsfile:**  
  Verifica il branch e che il file `Jenkinsfile` sia nella root del repository

- **Il sito non si apre:**  
  Controlla che:
  - i container siano “Up”
  - la porta 8000 sia esposta
  - il firewall non blocchi il traffico

---

# 9. Sicurezza

- Usa solo account GitHub tecnici/aziendali
- Ruota periodicamente i token di accesso (PAT)
- Mantieni Jenkins e i plugin sempre aggiornati
- Proteggi la VM e Jenkins con credenziali sicure e backup regolari

---

# 10. Accesso per i tecnici ARPAE

- Tutte le credenziali di servizio sono preconfigurate
- I tecnici devono solo:
  - Ricevere un utente Jenkins (web)
  - (Opzionale) Ricevere accesso SSH alla VM, se richiesto

---

# 11. Supporto

Per problemi o dubbi, contattare il team tecnico o aprire una issue nel repository GitHub.
