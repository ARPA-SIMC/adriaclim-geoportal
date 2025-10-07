// pipeline {
//     agent any

//     environment {
//         PROJECT_ROOT = 'adriaclim-master'
//         BACKEND_SERVICE = 'django'
//     }

//     stages {

//         stage('Inject Secrets') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     withCredentials([file(credentialsId: 'adria-env', variable: 'ENV_FILE')]) {
//                         sh '''
//                             echo "Copying .env file from Jenkins credentials" 
//                             cp "$ENV_FILE" .env
//                             echo ".env is ready"
//                         '''
//                     }
//                 }
//             }
//         }

//         stage('Cleanup Environment') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo "Cleaning up containers, volumes and orphans"
//                         docker compose down -v --remove-orphans || echo "No containers to stop"
//                     '''
//                     echo "Running docker system prune -af"
//                     sh 'docker system prune -af || echo "Nothing to clean"'
//                 }
//             }
//         }

//         stage('Build & Start Containers') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo "Building and starting all containers"
//                         docker compose up -d --build
//                         echo "Showing running containers..."
//                         docker compose ps
//                     '''
//                 }
//             }
//         }

//         stage('Run Django Tests') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo "Running Django test suite..."
//                         docker compose exec -T django python adria_project_backend/manage.py test tests
//                     '''
//                 }
//             }
//         }
//     }
// }
pipeline {
    agent any

    // 1. Definiamo i parametri: l'utente potrà scegliere quale branch buildare
    parameters {
        string(name: 'BRANCH_TO_BUILD', defaultValue: 'test_vm', description: 'Branch Git da cui eseguire il deploy')
        // Aggiunto parametro per l'URL del repo per non averlo hardcoded
        string(name: 'GIT_REPO_URL', defaultValue: 'git@github.com:tuo-utente/tuo-repo.git', description: 'URL del repository Git (preferibilmente SSH)')
    }
    
    options {
        // Aggiunta opzione di timeout per evitare che la build giri all'infinito
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        TEST_HOST = '172.19.99.37'
        SSH_USER  = 'fos'
        // 2. "Sanifichiamo" il nome del branch per usarlo nel path, sostituendo '/' con '-'
        SAFE_BRANCH_NAME = "${params.BRANCH_TO_BUILD.replaceAll('/', '-')}"
        REMOTE_PROJECT_PATH = "/home/fos/adriaclimplus-builds/${env.SAFE_BRANCH_NAME}"
    }

    stages {
        stage('Setup e Pulizia su VM di Test') {
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
                ]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
                            set -e # Ferma lo script al primo errore
                            
                            echo "Lavoro nella directory: ${env.REMOTE_PROJECT_PATH}"
                            mkdir -p ${env.REMOTE_PROJECT_PATH}
                            cd ${env.REMOTE_PROJECT_PATH}
                            
                            echo "[1] Pulizia ambiente Docker..."
                            if [ -f docker-compose.yml ]; then
                                docker compose down -v --remove-orphans || echo "Niente da fermare."
                            fi
                            docker system prune -af

                            echo "[2] Clono o aggiorno il codice per il branch: ${params.BRANCH_TO_BUILD}"
                            # NOTA: Per repository privati, assicurati che l'utente "${env.SSH_USER}" sulla VM "${env.TEST_HOST}"
                            # abbia accesso al repository Git (es. con una chiave SSH configurata in ~/.ssh/id_rsa)
                            if [ -d .git ]; then
                                git remote set-url origin ${params.GIT_REPO_URL}
                                git fetch --prune origin
                            else
                                git clone ${params.GIT_REPO_URL} .
                            fi
                            
                            git checkout ${params.BRANCH_TO_BUILD} || git checkout -b ${params.BRANCH_TO_BUILD} origin/${params.BRANCH_TO_BUILD}
                            git reset --hard origin/${params.BRANCH_TO_BUILD}
                            
                            echo "[3] PULIZIA CRITICA: Rimuovo tutti i file non tracciati"
                            git clean -fdx
                        '
                    """
                }
            }
        }
        
        stage('Inject Secrets e Build') {
            steps {
                withCredentials([
                    file(credentialsId: 'adria-env', variable: 'ENV_FILE'),
                    sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')
                ]) {
                    // Copio il file .env
                    sh """
                        echo "Invio il file .env alla VM"
                        scp -i ${SSH_KEY} -o StrictHostKeyChecking=no ${ENV_FILE} ${env.SSH_USER}@${env.TEST_HOST}:${env.REMOTE_PROJECT_PATH}/.env
                    """
                    // Eseguo la build
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
                            set -e
                            cd ${env.REMOTE_PROJECT_PATH}
                            echo "[4] Build & start dei container..."
                            docker compose up -d --build
                        '
                    """
                }
            }
        }
    }
    
    post {
        // Blocco che viene eseguito sempre, alla fine della build
        always {
            echo 'Build terminata.'
        }
        // Blocco eseguito solo se la build ha successo
        success {
            echo "Deploy del branch ${params.BRANCH_TO_BUILD} completato con successo."
        }
        // Blocco eseguito se la build fallisce
        failure {
            echo "ATTENZIONE: Deploy del branch ${params.BRANCH_TO_BUILD} fallito."
            // Azione opzionale: pulizia della directory remota in caso di fallimento
            // per garantire che la prossima build parta da zero.
            // withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
            //     sh "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} 'rm -rf ${env.REMOTE_PROJECT_PATH}'"
            // }
        }
    }
}

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

