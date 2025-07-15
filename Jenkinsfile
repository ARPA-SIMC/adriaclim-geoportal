pipeline {
  agent any

  environment {
    PROJECT_DIR = 'adriaclim-master'
    DOCKER_ENV_FILE = 'code/adria_project_backend/.env'
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
          bat """
            docker compose --env-file ${DOCKER_ENV_FILE} up -d
            docker compose --env-file ${DOCKER_ENV_FILE} exec django python adria_project_backend/manage.py test tests
          """
        }
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }
      }
      steps {
        echo "Lint checks skipped for now."
      }
    }

    stage('Optional Build Angular') {
      when {
        expression { return false }
      }
      steps {
        echo "Angular build skipped for now."
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir('adriaclim-master') {
        bat 'docker compose --env-file code/adria_project_backend/.env down || echo "Ignorato errore nel docker down"'
      }
      echo 'Pipeline completed without blocking on cleanup.'
    }
  }
}
