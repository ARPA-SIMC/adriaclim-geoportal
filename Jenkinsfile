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



