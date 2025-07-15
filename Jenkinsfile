pipeline {
  agent any

  environment {
    PROJECT_ROOT = 'adriaclim-master'
  }

  stages {

    stage('Checkout') {
      steps {
        echo "Repository checked out. Jenkins is ready."
      }
    }

    stage('Build & Run Containers') {
      steps {
        dir("${PROJECT_ROOT}") {
          bat '''
            echo === Building and starting containers ===
            docker compose up -d --build
          '''
        }
      }
    }

    stage('Run Django Tests') {
      steps {
        dir("${PROJECT_ROOT}") {
          bat '''
            echo === Running Django tests ===
            docker compose exec django python adria_project_backend/manage.py test tests
          '''
        }
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir('adriaclim-master') {
        bat 'docker compose down || echo "Ignoring docker down errors"'
      }
      echo 'Pipeline completed.'
    }
  }
}
