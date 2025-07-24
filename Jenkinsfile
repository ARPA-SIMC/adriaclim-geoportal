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

// pipeline {
//     agent any

//     environment {
//         PROJECT_ROOT = 'adriaclim-master'
//         BACKEND_SERVICE = 'django'
//         TEST_HOST = '172.19.99.37'       // IP della VM di test
//         SSH_USER  = 'fos'                // utente SSH sulla VM di test
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

//         stage('Cleanup Environment (locale, facoltativo)') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo "Cleaning up containers, volumes and orphans"
//                         docker compose down -v --remove-orphans || echo "No containers to stop"
//                         echo "Running docker system prune -af"
//                         docker system prune -af || echo "Nothing to clean"
//                     '''
//                 }
//             }
//         }

//         stage('Build & Start Containers (locale, facoltativo)') {
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

//         stage('Run Django Tests (locale, facoltativo)') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo "Running Django test suite..."
//                         docker compose exec -T django python adria_project_backend/manage.py test tests
//                     '''
//                 }
//             }
//         }

//         stage('Deploy su VM di Test (manuale)') {
//             steps {
//                 input message: "Vuoi eseguire il deploy sulla VM di test?", ok: "Deploy"
//                 withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
//                     sh """
//                         echo "Connessione a ${env.TEST_HOST} come ${env.SSH_USER}..."
//                         ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
//                             cd /percorso/progetto &&
//                             git pull &&
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
        TEST_HOST = '172.19.99.37'
        SSH_USER  = 'fos'
        REMOTE_PROJECT_PATH = '/home/fos/adriaclimplus-test'
    }

    stages {
        stage('Pulizia e Build su VM di Test') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
                            set -e
                            cd ${env.REMOTE_PROJECT_PATH} &&
                            echo "[1] Pulizia ambiente..." &&
                            docker compose down -v --remove-orphans || echo "Niente da pulire" &&
                            docker system prune -af || echo "Niente da pulire" &&
                            echo "[2] Aggiorno codice..." &&
                            git pull &&
                            echo "[3] Build & start dei container..." &&
                            docker compose up -d --build
                        '
                    """
                }
            }
        }

        stage('Test su VM di Test') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
                            set -e
                            cd ${env.REMOTE_PROJECT_PATH} &&
                            echo "[4] Eseguo i test Django..." &&
                            docker compose exec -T django python adria_project_backend/manage.py test tests
                        '
                    """
                }
            }
        }

        stage('Deploy (Restart/Update) su VM di Test') {
            when {
                expression {
                    // Questo fa sì che lo stage venga eseguito SOLO se lo stage "Test su VM di Test" è andato bene
                    currentBuild.resultIsBetterOrEqualTo('SUCCESS')
                }
            }
            steps {
                input message: "Vuoi completare il deploy (riavvio finale dei servizi) sulla VM di test?", ok: "Deploy"
                withCredentials([sshUserPrivateKey(credentialsId: 'test-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${env.SSH_USER}@${env.TEST_HOST} '
                            set -e
                            cd ${env.REMOTE_PROJECT_PATH} &&
                            echo "[5] Restart finale dei container (deploy concluso)..." &&
                            docker compose down -v --remove-orphans &&
                            docker compose up -d --build
                        '
                    """
                }
            }
        }
    }
}
