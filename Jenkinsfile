pipeline {
  agent any

  environment {
    PROJECT_DIR = 'code/adria_project_backend'
    ANGULAR_DIR = 'code/adria_project_frontend'
  }

  stages {

    stage('Start pipeline') {
      steps {
        echo "Repository checked out. Jenkins is ready."
      }
    }

    stage('Run Django Tests') {
      steps {
        dir("${PROJECT_DIR}") {
          // Usa il launcher py invece di python
          bat 'py manage.py test'
        }
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }
      }
      steps {
        echo "Linting checks (e.g., flake8)..."
      }
    }

    stage('Optional Build Angular') {
      when {
        expression { return false }
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
        expression { return false }
      }
      steps {
        bat 'docker compose up -d'
      }
    }
  }

  post {
    always {
      echo 'Pipeline completed.'
    }
  }
}
