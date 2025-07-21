// pipeline {
//     agent any

//     environment {
//         PROJECT_ROOT = 'adriaclim-master'
//         BACKEND_SERVICE = 'django'
//     }

//     stages {

//         stage('Inject Secrets') {
//                     steps {
//                         dir("${PROJECT_ROOT}") {
//                             withCredentials([file(credentialsId: 'adria-env', variable: 'ENV_FILE')]) {
//                                 sh '''
//                                     echo Copying .env file from Jenkins credentials
//                                     copy %ENV_FILE% .env
//                                     echo .env is ready
//                                 '''
//                             }
//                         }
//                     }
//                 }

//         stage('Cleanup Environment') {
//                 steps {
//                     dir("${PROJECT_ROOT}") {
//                         sh '''
//                             echo Cleaning up containers, volumes and orphans
//                             docker compose down -v --remove-orphans || echo "No containers to stop"
//                         '''
//                         echo "Running docker system prune -af"
//                         sh 'docker system prune -af || echo "Nothing to clean"'
//                     }
//                 }
//             }
                
//         stage('Build & Start Containers') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo Building and starting all containers
//                         docker compose up -d --build
//                         echo Showing running containers...
//                         docker compose ps
//                     '''
//                 }
//             }
//         }

//         stage('Run Django Tests') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     sh '''
//                         echo Running Django test suite...
//                         docker compose exec -T django python adria_project_backend/manage.py test tests
//                     '''
//                 }
//             }
//         }
//     }

// }

pipeline {
    agent any

    environment {
        PROJECT_ROOT = 'adriaclim-master'
        BACKEND_SERVICE = 'django'
    }

    stages {

        stage('Inject Secrets') {
            steps {
                dir("${PROJECT_ROOT}") {
                    withCredentials([file(credentialsId: 'adria-env', variable: 'ENV_FILE')]) {
                        sh '''
                            echo "Copying .env file from Jenkins credentials"
                            cp "$ENV_FILE" .env
                            echo ".env is ready"
                        '''
                    }
                }
            }
        }

        stage('Cleanup Environment') {
            steps {
                dir("${PROJECT_ROOT}") {
                    sh '''
                        echo "Cleaning up containers, volumes and orphans"
                        docker compose down -v --remove-orphans || echo "No containers to stop"
                    '''
                    echo "Running docker system prune -af"
                    sh 'docker system prune -af || echo "Nothing to clean"'
                }
            }
        }

        stage('Build & Start Containers') {
            steps {
                dir("${PROJECT_ROOT}") {
                    sh '''
                        echo "Building and starting all containers"
                        docker compose up -d --build
                        echo "Showing running containers..."
                        docker compose ps
                    '''
                }
            }
        }

        stage('Run Django Tests') {
            steps {
                dir("${PROJECT_ROOT}") {
                    sh '''
                        echo "Running Django test suite..."
                        docker compose exec -T django python adria_project_backend/manage.py test tests
                    '''
                }
            }
        }
    }
}

