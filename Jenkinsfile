pipeline {
    agent any

    environment {
        REMOTE_PROJECT_PATH_TEST = '/home/arpae/adriaclim-geoportal'
        REMOTE_PROJECT_PATH_PROD = '/home/arpae/adriaclim-geoportal'
    }

    stages {
        stage('Selezione host') {
            steps {
                script {
                    // Legge il file env-hosts.yml da Jenkins Config File Management
                    configFileProvider([configFile(fileId: 'env-hosts.yml', variable: 'CONFIG_FILE')]) {
                        def envYaml = readYaml file: "$CONFIG_FILE"
                        def hosts = []

                        if (env.GIT_BRANCH.contains('prod')) {
                            hosts = envYaml.hosts['prod']
                            env.DEPLOY_BRANCH = 'prod'
                        } else {
                            hosts = envYaml.hosts['test']
                            env.DEPLOY_BRANCH = 'test'
                        }

                        env.SSH_USER = 'arpae'
                        env.REMOTE_PROJECT_PATH = (env.DEPLOY_BRANCH == 'prod')
                            ? env.REMOTE_PROJECT_PATH_PROD
                            : env.REMOTE_PROJECT_PATH_TEST
                        env.SSH_CREDENTIAL_ID = 'arpae-ssh-key'
                        env.DEPLOY_HOST = hosts[0]

                        // Definizione condizionale di sudo e docker-compose
                        env.SUDO = (env.DEPLOY_BRANCH == 'prod') ? 'sudo' : ''
                        env.DOCKER = (env.DEPLOY_BRANCH == 'prod') ? 'sudo docker' : 'docker'
                        env.DOCKER_COMPOSE = (env.DEPLOY_BRANCH == 'prod') ? 'sudo docker-compose' : 'docker-compose'

                        echo "→ Deploy su ${env.DEPLOY_HOST} (${env.DEPLOY_BRANCH}) come utente ${env.SSH_USER}"
                    }
                }
            }
        }

        stage('Pulizia e aggiornamento codice') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            set -e
                            echo "[1] Pulizia ambiente su ${DEPLOY_HOST}..." &&
                            
                            if [ ! -d "${REMOTE_PROJECT_PATH}" ]; then
                                echo "[!] La directory ${REMOTE_PROJECT_PATH} non esiste. Eseguo git clone..." &&
                                cd \$(dirname ${REMOTE_PROJECT_PATH}) &&
                                git clone https://github.com/ARPA-SIMC/adriaclim-geoportal.git \$(basename ${REMOTE_PROJECT_PATH}) &&
                                cd ${REMOTE_PROJECT_PATH} &&
                                echo "[OK] Clone completato con successo."
                            fi

                            echo "[✓] Procedo con aggiornamento..." &&
                            cd ${REMOTE_PROJECT_PATH}/adriaclim-master &&

                            echo "[🧹 Stop e rimozione container precedenti...]" &&
                            sudo docker ps -aq | xargs -r sudo docker stop || true &&
                            sudo docker ps -aq | xargs -r sudo docker rm -f || true &&
                            sudo docker-compose down -v --remove-orphans || true &&
                            sudo docker system prune -af || true &&

                            echo "[2] Aggiorno codice da Git..." &&
                            cd ${REMOTE_PROJECT_PATH} &&
                            git fetch origin &&
                            git checkout ${DEPLOY_BRANCH} || git checkout -b ${DEPLOY_BRANCH} &&
                            git reset --hard origin/${DEPLOY_BRANCH}
                        '
                    """
                }
            }
        }

        stage('Inject Secrets (.env)') {
            steps {
                withCredentials([
                    file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
                    sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')
                ]) {
                    sh """
                        echo "[3] Invio .env su ${DEPLOY_HOST}"
                        scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${SSH_USER}@${DEPLOY_HOST}:/tmp/.env
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            mkdir -p ${REMOTE_PROJECT_PATH} &&
                            mv /tmp/.env ${REMOTE_PROJECT_PATH}/.env &&
                            chown ${SSH_USER}:${SSH_USER} ${REMOTE_PROJECT_PATH}/.env &&
                            chmod 600 ${REMOTE_PROJECT_PATH}/.env &&
                            echo "[OK] .env posizionato correttamente in ${REMOTE_PROJECT_PATH}"
                        '
                    """
                }
            }
        }

        stage('Deploy e build container') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')]) {
                script {
                    sh """
                    echo "[4] Avvio build e container su ${DEPLOY_HOST}"
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} bash -lc '
                        set -euo pipefail

                        echo "[git] Posizionamento repo..."
                        cd ${REMOTE_PROJECT_PATH}
                        git fetch --all --prune
                        git checkout ${DEPLOY_BRANCH}
                        git reset --hard origin/${DEPLOY_BRANCH}

                        echo "[secrets] Posiziono .env accanto a docker-compose.yml..."
                        if [ -f "${REMOTE_PROJECT_PATH}/.env" ]; then
                        cp -f ${REMOTE_PROJECT_PATH}/.env ${REMOTE_PROJECT_PATH}/adriaclim-master/.env
                        fi
                        ls -la ${REMOTE_PROJECT_PATH}/adriaclim-master/.env || true

                        echo "[frontend] Build Angular (production)..."
                        node -v || echo "Node non trovato"
                        npm -v || echo "NPM non trovato"
                        cd ${REMOTE_PROJECT_PATH}/adriaclim-master/code/adria_project_frontend
                        if [ -f package-lock.json ]; then
                        npm ci || npm install
                        else
                        npm install
                        fi
                        npx ng build --configuration=production --base-href=/
                        test -f dist/adria-project-front/index.html

                        echo "[docker] Rebuild immagini e avvio servizi..."
                        cd ${REMOTE_PROJECT_PATH}/adriaclim-master
                        # Info utili per il log (così vedi i nomi reali dei servizi)
                        ${DOCKER_COMPOSE} config --services || true

                        # Pull "best effort"
                        ${DOCKER_COMPOSE} pull || true

                        # Rebuild TUTTI i servizi definiti nel compose, senza elencarli (evita 'No such service')
                        ${DOCKER_COMPOSE} build --no-cache

                        # Avvio e creazione network se mancante, rimuovendo eventuali orfani
                        ${DOCKER_COMPOSE} up -d --remove-orphans

                        echo "[health] Controlli rapidi..."
                        ${DOCKER} ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                        echo "[probe] Verifico Nginx risponda su 8000..."
                        if curl -sfI http://localhost:8000/ >/dev/null 2>&1; then
                        echo "[OK] Nginx risponde correttamente"
                        else
                        echo "[ERRORE] Nginx non risponde"
                        exit 1
                        fi

                        echo "[OK] Deploy completato su ${DEPLOY_HOST}"
                    '
                    """
                }
            }
        }
    }
}
}




