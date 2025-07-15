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

    stage('Run Tests') {
      steps {
        dir("${PROJECT_ROOT}") {
          withCredentials([
            string(credentialsId: 'SECRET_KEY', variable: 'SECRET_KEY'),
            string(credentialsId: 'POSTGRES_NAME', variable: 'POSTGRES_NAME'),
            string(credentialsId: 'POSTGRES_USER', variable: 'POSTGRES_USER'),
            string(credentialsId: 'POSTGRES_PASSWORD', variable: 'POSTGRES_PASSWORD')
          ]) {
            bat '''
              echo === Starting containers with injected credentials ===
              docker compose up -d
              echo === Running Django tests ===
              docker compose exec django python adria_project_backend/manage.py test tests
            '''
          }
        }
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir('adriaclim-master') {
        bat '''
          docker compose down || echo "Ignoring docker down errors"
        '''
      }
      echo 'Pipeline completed.'
    }
  }
}
