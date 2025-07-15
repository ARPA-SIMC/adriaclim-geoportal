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

    stage('Start Docker containers') {
      steps {
        echo "Starting Docker containers..."
        bat 'docker compose up -d'
      }
    }

    stage('Run Django Tests in Docker') {
      steps {
        echo "Running Django tests inside Docker container..."
        bat 'docker compose exec django python adria_project_backend/manage.py test tests'
      }
    }

    stage('Optional Lint Checks') {
      when {
        expression { return false }
      }
      steps {
        echo "Linting checks (e.g., flake8)..."
      }
    }

  }

  post {
    always {
      echo 'Stopping Docker containers...'
      bat 'docker compose down'
      echo 'Pipeline completed.'
    }
  }
}
