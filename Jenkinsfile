pipeline {
  agent any

  stages {

    stage('Start pipeline') {
      steps {
        echo "Repository checked out. Jenkins is ready."
      }
    }

    stage('Start Docker containers') {
      steps {
        echo "Starting Docker containers..."
        dir('adriaclim-master') {
          bat 'docker compose up -d'
        }
      }
    }

    stage('Run Django Tests in Docker') {
      steps {
        echo "Running Django tests inside Docker container..."
        dir('adriaclim-master') {
          bat 'docker compose exec django python adria_project_backend/manage.py test tests'
        }
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
