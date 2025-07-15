pipeline {
  agent any

  environment {
    PROJECT_DIR = 'code/adria_project_backend'
  }

  stages {

    stage('Start pipeline') {
      steps {
        echo "Repository checked out. Jenkins is ready."
      }
    }

    stage('Run Django Tests in Docker') {
      steps {
        withCredentials([
          string(credentialsId: 'POSTGRES_NAME', variable: 'POSTGRES_NAME'),
          string(credentialsId: 'POSTGRES_USER', variable: 'POSTGRES_USER'),
          string(credentialsId: 'POSTGRES_PASSWORD', variable: 'POSTGRES_PASSWORD'),
          string(credentialsId: 'DJANGO_SECRET_KEY', variable: 'SECRET_KEY')
        ]) {
          dir('adriaclim-master') {
            bat '''
              docker compose up -d
              docker compose exec django python adria_project_backend/manage.py test tests || exit 1
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
        bat 'docker compose down || echo "Ignoro errore nel docker down"'
      }
      echo 'Pipeline completed.'
    }
  }
}
