pipeline {
    agent any

    parameters {
        string(name: 'WAIT_MINUTES', defaultValue: '20', description: 'Wait time after build (in minutes)')
        string(name: 'MAIL_RECIPIENTS', defaultValue: 'you@example.com', description: 'Email recipients (if configured)')
        booleanParam(name: 'DOCKER_PRUNE', defaultValue: false, description: 'Run docker system prune -af before build?')
    }

    environment {
        PROJECT_ROOT = 'adriaclim-master'
        BACKEND_SERVICE = 'django'
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out the repository..."
                // If this pipeline is linked to SCM:
                checkout scm
            }
        }

        stage('Inject Secrets') {
            steps {
                dir("${PROJECT_ROOT}") {
                    withCredentials([file(credentialsId: 'adria-env', variable: 'ENV_FILE')]) {
                        bat '''
                            echo Copying .env file from Jenkins secret
                            copy %ENV_FILE% .env
                            echo .env is ready
                        '''
                    }
                }
            }
        }

        stage('Cleanup Environment') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo === Cleaning up containers, volumes and orphans ===
                        docker compose down -v --remove-orphans || echo "No containers to stop"
                    '''
                }
                script {
                    if (params.DOCKER_PRUNE) {
                        echo "Running docker system prune -af"
                        bat 'docker system prune -af || echo "Nothing to clean"'
                    } else {
                        echo "⏭Skipping docker system prune"
                    }
                }
            }
        }

        stage('Build & Start Containers') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo === Building and starting containers ===
                        docker compose up -d --build
                    '''
                }
            }
        }

        stage('Wait for Containers to Initialize') {
            steps {
                script {
                    echo "Waiting ${params.WAIT_MINUTES} minutes for containers to initialize..."
                    sleep(time: params.WAIT_MINUTES.toInteger(), unit: 'MINUTES')
                }
            }
        }

        stage('Verify Containers Status') {
            steps {
                dir("${PROJECT_ROOT}") {
                    script {
                        for (int i = 1; i <= 3; i++) {
                            echo "Checking container status (${i}/3)..."
                            bat 'docker compose ps'
                            
                            if (i < 3) {
                                echo "Waiting 30 seconds before next check..."
                                sleep(time: 30, unit: 'SECONDS')
                            }
                        }
                    }
                }
            }
        }

        stage('Run Django Tests') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo === Running Django test suite ===
                        docker compose exec django python adria_project_backend/manage.py test tests
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed SUCCESSFULLY.'
            emailext (
                subject: "SUCCESS: Jenkins pipeline completed",
                body: "All containers are running and Django tests passed successfully.",
                to: "${params.MAIL_RECIPIENTS}"
            )
        }
        failure {
            echo 'Pipeline FAILED.'
            emailext (
                subject: "FAILURE: Jenkins pipeline failed",
                body: "One or more stages failed. Please check Jenkins logs for details.",
                to: "${params.MAIL_RECIPIENTS}"
            )
        }
        always {
            echo 'Final cleanup: stopping containers...'
            dir("${PROJECT_ROOT}") {
                bat 'docker compose down || echo "Ignoring errors in final docker down"'
            }
        }
    }
}
