// pipeline {
//     agent any

//     environment {
//         REMOTE_PROJECT_PATH_TEST = '/home/arpae/adriaclimplus-test/adriaclim-master'
//         REMOTE_PROJECT_PATH_PROD = '/home/arpae/adriaclim-geoportal'
//     }

//     stages {
//         stage('Selezione host') {
//             steps {
//                 script {
//                     // Legge il file env-hosts.yml da Jenkins Config File Management
//                     configFileProvider([configFile(fileId: 'env-hosts.yml', variable: 'CONFIG_FILE')]) {
//                         def envYaml = readYaml file: "$CONFIG_FILE"
//                         def hosts = []

//                         if (env.GIT_BRANCH.contains('prod')) {
//                             hosts = envYaml.hosts['prod']
//                             env.DEPLOY_BRANCH = 'prod'
//                             env.SSH_USER = 'arpae'
//                             env.REMOTE_PROJECT_PATH = env.REMOTE_PROJECT_PATH_PROD
//                             env.SSH_CREDENTIAL_ID = 'arpae-ssh-key'
//                         } else {
//                             hosts = envYaml.hosts['test']
//                             env.DEPLOY_BRANCH = 'test'
//                             env.SSH_USER = 'arpae'
//                             env.REMOTE_PROJECT_PATH = env.REMOTE_PROJECT_PATH_TEST
//                             env.SSH_CREDENTIAL_ID = 'arpae-ssh-key'
//                         }

//                         env.DEPLOY_HOST = hosts[0]
//                         echo "→ Deploy su ${env.DEPLOY_HOST} (${env.DEPLOY_BRANCH}) come utente ${env.SSH_USER}"
//                     }
//                 }
//             }
//         }

//         stage('Pulizia e aggiornamento codice') {
//             steps {
//                 withCredentials([sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')]) {
//                     sh """
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
//                             set -e
//                             echo "[1] Pulizia ambiente su ${DEPLOY_HOST}..." &&
                            
//                             if [ ! -d "${REMOTE_PROJECT_PATH}" ]; then
//                                 echo "[!] La directory ${REMOTE_PROJECT_PATH} non esiste. Eseguo git clone..." &&
//                                 cd \$(dirname ${REMOTE_PROJECT_PATH}) &&
//                                 git clone https://github.com/ARPA-SIMC/adriaclim-geoportal.git \$(basename ${REMOTE_PROJECT_PATH}) &&
//                                 cd ${REMOTE_PROJECT_PATH} &&
//                                 echo "[OK] Clone completato con successo."
//                             fi

//                             echo "[✓] Procedo con aggiornamento..." &&
//                             cd ${REMOTE_PROJECT_PATH}/adriaclim-master &&

//                             echo "[🧹 Stop e rimozione container precedenti...]" &&
//                             sudo docker ps -aq | xargs -r sudo docker stop || true &&
//                             sudo docker ps -aq | xargs -r sudo docker rm -f || true &&
//                             sudo docker-compose down -v --remove-orphans || true &&
//                             sudo docker system prune -af || true &&

//                             echo "[2] Aggiorno codice da Git..." &&
//                             cd ${REMOTE_PROJECT_PATH} &&
//                             git fetch origin &&
//                             git checkout ${DEPLOY_BRANCH} || git checkout -b ${DEPLOY_BRANCH} &&
//                             git reset --hard origin/${DEPLOY_BRANCH}
//                         '
//                     """
//                 }
//             }
//         }

//         stage('Inject Secrets (.env)') {
//             steps {
//                 withCredentials([
//                     file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
//                     sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         echo "[3] Invio .env su ${DEPLOY_HOST}"
//                         scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${SSH_USER}@${DEPLOY_HOST}:/tmp/.env
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
//                             mkdir -p ${REMOTE_PROJECT_PATH} &&
//                             mv /tmp/.env ${REMOTE_PROJECT_PATH}/.env &&
//                             chown ${SSH_USER}:${SSH_USER} ${REMOTE_PROJECT_PATH}/.env &&
//                             chmod 600 ${REMOTE_PROJECT_PATH}/.env &&
//                             echo "[OK] .env posizionato correttamente in ${REMOTE_PROJECT_PATH}"
//                         '
//                     """
//                 }
//             }
//         }

//         stage('Deploy e build container') {
//             steps {
//                 withCredentials([sshUserPrivateKey(credentialsId: "${env.SSH_CREDENTIAL_ID}", keyFileVariable: 'SSH_KEY')]) {
//                     sh """
//                         echo "[4] Avvio build e container su ${DEPLOY_HOST}"
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
//                             set -e
//                             cd ${REMOTE_PROJECT_PATH}/adriaclim-master &&
//                             echo "[docker-compose] Build & start..." &&
//                             sudo docker-compose --env-file ../.env up -d --build &&
//                             echo "[✔] Deploy completato su ${DEPLOY_HOST} (${DEPLOY_BRANCH})"
//                         '
//                     """
//                 }
//             }
//         }
//     }
// }

pipeline {
    agent any

    environment {
        REMOTE_PROJECT_PATH_TEST = '/home/arpae/adriaclimplus-test/adriaclim-master'
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
                            echo "[1] Pulizia ambiente su ${DEPLOY_HOST}..."

                            # Se la cartella non esiste, la creo e clono il repository
                            if [ ! -d "${REMOTE_PROJECT_PATH}" ]; then
                                echo "[!] La directory ${REMOTE_PROJECT_PATH} non esiste. Eseguo git clone..." &&
                                mkdir -p \$(dirname \${REMOTE_PROJECT_PATH}) &&
                                cd \$(dirname \${REMOTE_PROJECT_PATH}) &&
                                git clone https://github.com/ARPA-SIMC/adriaclim-geoportal.git \${REMOTE_PROJECT_PATH} &&
                                echo "[OK] Clone completato con successo."
                            fi

                            echo "[✓] Procedo con aggiornamento..."
                            cd ${REMOTE_PROJECT_PATH}

                            echo "[🧹 Stop e rimozione container precedenti...]"
                            sudo docker ps -aq | xargs -r sudo docker stop || true
                            sudo docker ps -aq | xargs -r sudo docker rm -f || true
                            sudo docker-compose down -v --remove-orphans || true
                            sudo docker system prune -af || true

                            echo "[2] Aggiorno codice da Git..."
                            git fetch origin
                            git checkout ${DEPLOY_BRANCH} || git checkout -b ${DEPLOY_BRANCH}
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
                    sh """
                        echo "[4] Avvio build e container su ${DEPLOY_HOST}"
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            set -e
                            cd ${REMOTE_PROJECT_PATH}/adriaclim-master &&
                            echo "[docker-compose] Build & start..." &&
                            ${DOCKER_COMPOSE} --env-file ../.env up -d --build &&
                            echo "[✔] Deploy completato su ${DEPLOY_HOST} (${DEPLOY_BRANCH})"
                        '
                    """
                }
            }
        }
    }
}



