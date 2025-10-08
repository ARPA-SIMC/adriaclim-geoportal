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

    environment {
        SSH_USER = 'fos'
        TEST_HOST = '172.19.99.37'
        PROD_HOST = '172.19.99.34'
        REMOTE_PROJECT_PATH = '/home/fos/adriaclimplus-test/adriaclim-master'
    }

    stages {
        stage('Selezione host') {
            steps {
                script {
                    if (env.GIT_BRANCH.contains('prod')) {
                        env.DEPLOY_HOST = PROD_HOST
                        env.DEPLOY_BRANCH = 'prod'
                    } else {
                        env.DEPLOY_HOST = TEST_HOST
                        env.DEPLOY_BRANCH = 'test'
                    }
                    echo "→ Deploy su ${DEPLOY_HOST} (branch ${DEPLOY_BRANCH})"
                }
            }
        }

        stage('Pulizia e aggiornamento codice') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            set -e
                            echo "[1] Pulizia ambiente su ${DEPLOY_HOST}..." &&
                            mkdir -p ${REMOTE_PROJECT_PATH} &&
                            cd ${REMOTE_PROJECT_PATH} &&
                            docker compose down -v --remove-orphans || true &&
                            docker system prune -af || true &&
                            echo "[2] Aggiorno codice..." &&
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
                    sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
                ]) {
                    sh """
                        echo "[3] Invio .env su ${DEPLOY_HOST}"
                        scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${SSH_USER}@${DEPLOY_HOST}:/tmp/.env
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            mkdir -p ${REMOTE_PROJECT_PATH} &&
                            mv /tmp/.env ${REMOTE_PROJECT_PATH}/.env &&
                            chown fos:fos ${REMOTE_PROJECT_PATH}/.env &&
                            chmod 600 ${REMOTE_PROJECT_PATH}/.env &&
                            echo "[OK] .env posizionato correttamente in ${REMOTE_PROJECT_PATH}"
                        '
                    """
                }
            }
        }

        stage('Deploy e build container') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        echo "[4] Avvio build e container su ${DEPLOY_HOST}"
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${DEPLOY_HOST} '
                            set -e
                            cd ${REMOTE_PROJECT_PATH} &&
                            echo "[Docker Compose] Build & start..." &&
                            docker compose --env-file .env up -d --build
                        '
                    """
                }
            }
        }
    }
}



