pipeline {
  agent any

  environment {
    COMPOSE_ENV = 'code/adria_project_backend/.env'
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
          bat """
          docker compose --env-file %COMPOSE_ENV% up -d
          docker compose --env-file %COMPOSE_ENV% exec django python adria_project_backend/manage.py test tests
          """
        }
      }
    }

    stage('Optional Lint Checks') {
      when { expression { return false } }
      steps {
        echo "Lint checks skipped"
      }
    }

    stage('Optional Build Angular') {
      when { expression { return false } }
      steps {
        echo "Angular build skipped"
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir('adriaclim-master') {
        bat """
        docker compose --env-file %COMPOSE_ENV% down || echo "Ignoro errore nel docker down"
        """
      }
      echo 'Pipeline completed without blocking on cleanup.'
    }
  }
}
