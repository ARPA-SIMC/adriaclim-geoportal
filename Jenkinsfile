pipeline {
  agent any

  environment {
    PROJECT_DIR = 'code/adria_project_backend'   // Percorso backend Django
    ANGULAR_DIR = 'code/adria_project_frontend'  // Percorso frontend Angular
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
          // Su Windows usiamo bat invece di sh
          bat 'python manage.py test'
        }
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }  // Può essere attivato in futuro
      }
      steps {
        echo "Linting checks (e.g., flake8)..."
        // bat 'flake8 .'
      }
    }

    stage('Optional Build Angular') {
      when {
        expression { return false }  // Disattivato per ora
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
        expression { return false }  // Disattivato per ora
      }
      steps {
        bat 'docker compose up -d'
      }
    }
  }

  post {
    always {
      echo 'Pipeline completed.'
      // Su Windows evitiamo docker stop se non serve
      // bat 'docker compose down || true'
    }
  }
}
