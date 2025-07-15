pipeline {
  agent any

  environment {
    PROJECT_DIR = 'adriaclim-master'          // directory principale del progetto
    DOCKER_COMPOSE_FILE = 'docker-compose.yml'
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
          echo "🚀 Avvio dei container Docker..."
          // Avvio container necessari
          bat 'docker compose up -d'

          echo "🧪 Esecuzione test Django all’interno del container..."
          // Esegue i test Django dentro il container `django`
          bat 'docker compose exec django python adria_project_backend/manage.py test tests'
        }
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }  // Potrai attivarli in futuro
      }
      steps {
        echo "🔍 Linting checks (flake8, ecc.)..."
      }
    }

    stage('Optional Build Angular') {
      when {
        expression { return false }  // Disattivato per ora
      }
      steps {
        dir("${PROJECT_DIR}/code/adria_project_frontend") {
          bat 'npm install'
          bat 'ng build --configuration production'
        }
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir("${PROJECT_DIR}") {
        // Chiude i container senza far fallire la pipeline in caso di warning
        bat 'docker compose down || exit 0'
      }
      echo 'Pipeline completed.'
    }
  }
}
