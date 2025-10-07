// jenkinsfile per test funzionante

// pipeline {
//     agent any

//     environment {
//         TEST_HOST = '172.19.99.37'
//         SSH_USER  = 'fos'
//         REMOTE_PROJECT_PATH = '/home/fos/adriaclimplus-test/adriaclim-master'
//     }

//     stages {
//         stage('Inject Secrets su VM di Test') {
//             steps {
//                 withCredentials([
//                     file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
//                     sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         echo "Invio il file .env alla VM di test"
//                         scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${env.SSH_USER}@${env.TEST_HOST}:${env.REMOTE_PROJECT_PATH}/.env
//                     """
//                 }
//             }
//         }

//         stage('Pulizia e Build su VM di Test') {
//             steps {
//                 withCredentials([
//                     sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
//                             set -e
//                             cd ${env.REMOTE_PROJECT_PATH} &&
//                             echo "[1] Pulizia ambiente..." &&
//                             docker compose down -v --remove-orphans || echo "Niente da pulire" &&
//                             docker system prune -af || echo "Niente da pulire" &&
//                             echo "[2] Aggiorno codice (forzato su test_vm)..." &&
//                             git fetch origin &&
//                             git checkout test_vm || git checkout -b test_vm &&
//                             git reset --hard origin/test_vm &&
//                             echo "[3] Build & start dei container..." &&
//                             docker compose up -d --build
//                         '
//                     """
//                 }
//             }
//         }

//         // stage('Test su VM di Test') {
//         //     steps {
//         //         withCredentials([
//         //             sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
//         //         ]) {
//         //             sh """
//         //                 ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
//         //                     set -e
//         //                     cd ${REMOTE_PROJECT_PATH} &&
//         //                     echo "[4] Eseguo i test Django..." &&
//         //                     docker compose exec -T django python adria_project_backend/manage.py test tests
//         //                 '
//         //             """
//         //         }
//         //     }
//         // }

//         stage('Deploy (Restart/Update) su VM di Test') {
//             when {
//                 expression {
//                     currentBuild.resultIsBetterOrEqualTo('SUCCESS')
//                 }
//             }
//             steps {
//                 withCredentials([
//                     sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
//                             set -e
//                             cd ${REMOTE_PROJECT_PATH} &&
//                             echo "[5] Restart finale dei container (deploy concluso)..." &&
//                             docker compose down -v --remove-orphans &&
//                             docker compose up -d --build
//                         '
//                     """
//                 }
//             }
//         }
//     }
// }


// jenkinsfile per produzione

// pipeline {
//     agent any

//     environment {
//         DEV_HOST = '172.19.99.37'
//         DEV_USER = 'fos'
//         DEV_PROJECT_PATH = '/home/fos/adriaclimplus-test/adriaclim-master'
//         PROD_HOST = 'IP_PRODUZIONE'
//         PROD_USER = 'nomeutente'
//         PROD_PROJECT_PATH = '/home/nomeutente/adriaclimplus-prod/adriaclim-master'
//     }

//     stages {
//         stage('Deploy su DEV (Test)') {
//             when {
//                 not {
//                     branch 'prod'
//                 }
//             }
//             steps {
//                 withCredentials([
//                     file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
//                     sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         echo "Invio il file .env alla VM di test"
//                         scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${DEV_USER}@${DEV_HOST}:${DEV_PROJECT_PATH}/.env

//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${DEV_USER}@${DEV_HOST} '
//                             set -e
//                             cd ${DEV_PROJECT_PATH} &&
//                             echo "[1] Pulizia ambiente..." &&
//                             docker compose down -v --remove-orphans || echo "Niente da pulire" &&
//                             docker system prune -af || echo "Niente da pulire" &&
//                             echo "[2] Aggiorno codice..." &&
//                             git pull &&
//                             echo "[3] Build & start dei container..." &&
//                             docker compose up -d --build &&
//                             echo "[4] Eseguo i test Django..." &&
//                             docker compose exec -T django python adria_project_backend/manage.py test tests &&
//                             echo "[5] Restart finale dei container (deploy concluso)..." &&
//                             docker compose down -v --remove-orphans &&
//                             docker compose up -d --build
//                         '
//                     """
//                 }
//             }
//         }

//         stage('Deploy su PROD (Produzione)') {
//             when {
//                 branch 'prod'
//             }
//             steps {
//                 script {
//                     input message: "Sei sicura di voler eseguire il deploy in PRODUZIONE?", ok: "Sì, deploy in prod"
//                 }
//                 withCredentials([
//                     file(credentialsId: 'adria-env-prod', variable: 'ENV_FILE'),
//                     sshUserPrivateKey(credentialsId: 'prod-ssh-key', keyFileVariable: 'SSH_KEY')
//                 ]) {
//                     sh """
//                         echo "Invio il file .env alla VM di produzione"
//                         scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${PROD_USER}@${PROD_HOST}:${PROD_PROJECT_PATH}/.env

//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} '
//                             set -e
//                             cd ${PROD_PROJECT_PATH} &&
//                             echo "[1] Pulizia ambiente..." &&
//                             docker compose down -v --remove-orphans || echo "Niente da pulire" &&
//                             docker system prune -af || echo "Niente da pulire" &&
//                             echo "[2] Aggiorno codice..." &&
//                             git pull &&
//                             echo "[3] Build & start dei container..." &&
//                             docker compose up -d --build &&
//                             echo "[4] Eseguo i test Django..." &&
//                             docker compose exec -T django python adria_project_backend/manage.py test tests &&
//                             echo "[5] Restart finale dei container (deploy concluso)..." &&
//                             docker compose down -v --remove-orphans &&
//                             docker compose up -d --build
//                         '
//                     """
//                 }
//             }
//         }
//     }
// }

pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        SSH_USER  = 'fos'
        REMOTE_PROJECT_PATH = '/home/fos/adriaclimplus-test/adriaclim-master'
    }

    parameters {
        string(name: 'BRANCH_TO_BUILD', defaultValue: 'test', description: 'Branch da buildare (test o prod)')
    }

    stages {

        // 1️ Selezione host in base al branch
        stage('Selezione host') {
            steps {
                script {
                    configFileProvider([configFile(fileId: 'env-hosts.yml', variable: 'CONFIG_FILE')]) {
                        def envYaml = readYaml file: "${CONFIG_FILE}"
                        def hosts = []

                        if (params.BRANCH_TO_BUILD.contains('prod')) {
                            hosts = envYaml.hosts['prod']
                            env.TARGET_HOST = hosts[0]
                            env.ENV_TYPE = 'prod'
                        } else {
                            hosts = envYaml.hosts['test']
                            env.TARGET_HOST = hosts[0]
                            env.ENV_TYPE = 'test'
                        }

                        echo "Branch: ${params.BRANCH_TO_BUILD}"
                        echo "Ambiente: ${env.ENV_TYPE}"
                        echo "Host selezionato: ${env.TARGET_HOST}"
                    }
                }
            }
        }

        // 2️ Copia file .env sulla macchina corretta
        stage('Inject Secrets su VM') {
            steps {
                withCredentials([
                    file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
                    sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
                ]) {
                    sh(label: "Invio file .env", script: '''
                        echo "Invio .env"
                        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$TARGET_HOST" "mkdir -p $REMOTE_PROJECT_PATH && chown -R $SSH_USER:$SSH_USER $REMOTE_PROJECT_PATH"
                        scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$ENV_FILE" "$SSH_USER@$TARGET_HOST:/tmp/.env"
                        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$TARGET_HOST" "sudo mv /tmp/.env $REMOTE_PROJECT_PATH/.env && sudo chown $SSH_USER:$SSH_USER $REMOTE_PROJECT_PATH/.env"
                    ''')
                }
            }
        }


        // 3 Pulizia totale + build da zero
        stage('Pulizia e Build su VM') {
            steps {
                script {
                    sshagent(credentials: ['test-ssh-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${SSH_USER}@${TARGET_HOST} '
                                set -Eeuo pipefail
                                echo "[0] Rimozione completa vecchia directory..."
                                rm -rf ${REMOTE_PROJECT_PATH}
                                mkdir -p ${REMOTE_PROJECT_PATH}
                                cd ${REMOTE_PROJECT_PATH}

                                echo "[1] 🧹 Pulizia ambiente Docker..."
                                docker compose down -v --remove-orphans || true
                                docker system prune -af || true

                                echo "[2] Clono e aggiorno il codice..."
                                git clone --origin origin git@github.com:TUO_ORG/TUO_REPO.git .
                                git fetch origin
                                git checkout ${params.BRANCH_TO_BUILD} || git checkout -b ${params.BRANCH_TO_BUILD}
                                git reset --hard origin/${params.BRANCH_TO_BUILD}
                                git clean -fdx

                                echo "[3] Build & start dei container..."
                                COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \\
                                docker compose up -d --build
                            '
                        """
                    }
                }
            }
        }

        // Riavvio finale (deploy)
        stage('Restart finale dei container') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${TARGET_HOST} '
                            set -e
                            cd ${REMOTE_PROJECT_PATH}
                            echo "[4] Restart finale dei container..."
                            docker compose down -v --remove-orphans
                            docker compose up -d --build
                        '
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deploy completato con successo su ${env.TARGET_HOST} (${env.ENV_TYPE})"
        }
        failure {
            echo "Deploy fallito su ${env.TARGET_HOST} (${env.ENV_TYPE})"
        }
    }
}
