pipeline {
  agent any

  environment {
    // Percorsi di progetto
    PROJECT_DIR = 'adriaclim-master'
    BACKEND_DIR = 'adriaclim-master/code/adria_project_backend'
    ANGULAR_DIR = 'adriaclim-master/code/adria_project_frontend'
  }

  stages {

    stage('Start pipeline') {
      steps {
        echo 'Repository checked out. Jenkins is ready.'
      }
    }

    stage('Run Django Tests') {
      steps {
        dir("${PROJECT_DIR}") {
          echo 'Starting Django tests inside Docker containers...'
          bat 'docker compose up -d'
          bat 'docker compose exec django python adria_project_backend/manage.py test tests'
        }
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }  // Disattivato per ora
      }
      steps {
        echo 'Running lint checks (flake8)...'
        // bat 'flake8 .'
      }
    }

    stage('Optional Build Angular') {
      when {
        expression { return false }  // Disattivato per ora
      }
      steps {
        dir("${ANGULAR_DIR}") {
          echo '🛠 Building Angular frontend...'
          bat 'npm install'
          bat 'ng build --configuration production'
        }
      }
    }

    stage('Optional Run Docker') {
      when {
        expression { return false }  // Disattivato per ora
      }
      steps {
        dir("${PROJECT_DIR}") {
          echo 'Running full Docker environment...'
          bat 'docker compose up -d'
        }
      }
    }
  }

  post {
    always {
      echo 'Stopping Docker containers...'
      dir("${PROJECT_DIR}") {
        bat '''
          docker compose down || echo "⚠️ Docker down returned non-zero but ignored."
          exit 0
        '''
      }
      echo 'Pipeline completed without blocking on cleanup.'
    }
  }
}
