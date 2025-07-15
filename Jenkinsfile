pipeline {
    agent any

    environment {
        PROJECT_DIR = 'adriaclim-master/code/adria_project_backend'  // Percorso backend Django
        ANGULAR_DIR = 'adriaclim-master/code/adria_project_frontend' // Percorso frontend Angular
    }

    stages {

        stage('Start pipeline') {
            steps {
                echo "Repository checked out. Jenkins is ready."
            }
        }

        stage('Run Django Tests') {
            steps {
                dir('adriaclim-master') {
                    bat 'docker compose up -d'
                    bat 'docker compose exec django python adria_project_backend/manage.py test tests'
                }
            }
        }

        stage('Optional Lint Checks') {
            when {
                expression { return false } // Disattivato per ora
            }
            steps {
                echo "Linting checks (e.g., flake8)..."
                // bat 'flake8 .'
            }
        }

        stage('Optional Build Angular') {
            when {
                expression { return false } // Disattivato per ora
            }
            steps {
                dir("${ANGULAR_DIR}") {
                    bat 'npm install'
                    bat 'ng build --configuration production'
                }
            }
        }

        stage('Optional Run Docker') {
            when {
                expression { return false } // Disattivato per ora
            }
            steps {
                bat 'docker compose up -d'
            }
        }
    }

    post {
        always {
            echo 'Stopping Docker containers...'
            dir('adriaclim-master') {
                bat 'docker compose down || exit 0'
            }
            echo 'Pipeline completed.'
        }
    }
}
