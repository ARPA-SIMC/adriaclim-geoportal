pipeline {
  agent any

  environment {
    PROJECT_ROOT = 'adriaclim-master'
    ENV_FILE = '../.env.jenkins'   // relativo alla root Jenkins
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
          bat '''
            echo === Starting containers with pre-existing .env.jenkins ===
            docker compose --env-file %ENV_FILE% up -d --build

            echo === Running Django tests inside a fresh container ===
            docker compose run --rm --env-file %ENV_FILE% django python adria_project_backend/manage.py test tests
          '''
        }
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir('adriaclim-master') {
        bat '''
          docker compose --env-file %ENV_FILE% down || echo "Ignoring docker down errors"
        '''
      }
      echo 'Pipeline completed.'
    }
  }
}
