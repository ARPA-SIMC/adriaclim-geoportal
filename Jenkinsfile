pipeline {
    agent any

    parameters {
        string(name: 'MAIL_RECIPIENTS', defaultValue: 'you@example.com', description: 'Email recipients for notifications')
        booleanParam(name: 'DOCKER_PRUNE', defaultValue: false, description: 'Run docker system prune -af before build?')
    }

    environment {
        PROJECT_ROOT = 'adriaclim-master'
        BACKEND_SERVICE = 'django'
        HEALTHCHECK_URL = 'http://localhost:8000'
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out the repository..."
                checkout scm
            }
        }

        stage('Inject Secrets') {
            steps {
                dir("${PROJECT_ROOT}") {
                    withCredentials([file(credentialsId: 'adria-env', variable: 'ENV_FILE')]) {
                        bat '''
                            echo Copying .env file from Jenkins credentials
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
                        echo 🧹 Cleaning up containers, volumes and orphans
                        docker compose down -v --remove-orphans || echo "No containers to stop"
                    '''
                }
                script {
                    if (params.DOCKER_PRUNE) {
                        echo "Running docker system prune -af"
                        bat 'docker system prune -af || echo "Nothing to clean"'
                    } else {
                        echo "Skipping docker system prune"
                    }
                }
            }
        }

        stage('Build & Start Containers') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo Building and starting all containers
                        docker compose up -d --build
                    '''
                }
            }
        }

        stage('Wait for Django Healthcheck') {
            steps {
                script {
                    def maxRetries = 30 // 30 attempts x 10s = 5 minutes max wait
                    def started = false

                    for (int i = 1; i <= maxRetries; i++) {
                        echo "Healthcheck attempt ${i}/${maxRetries}..."

                        def httpCode = bat(
                            returnStdout: true,
                            script: "curl -s -o NUL -w %%{http_code} ${HEALTHCHECK_URL}"
                        ).trim()

                        if (httpCode == "200") {
                            echo "Django is healthy!"
                            started = true
                            break
                        } else {
                            echo "Django not ready yet (HTTP ${httpCode}), waiting 10 seconds..."
                            sleep(time: 10, unit: 'SECONDS')
                        }
                    }

                    if (!started) {
                        error("Django did NOT become healthy within 5 minutes.")
                    } else {
                        echo "Django responded, waiting extra 15 seconds to ensure migrator is done..."
                        sleep(time: 15, unit: 'SECONDS') // extra wait for migrator to finish
                    }
                }
            }
        }

        stage('Verify Containers Status') {
            steps {
                dir("${PROJECT_ROOT}") {
                    echo "Checking container status..."
                    bat 'docker compose ps'
                }
            }
        }

        stage('Run Django Tests') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo Running Django test suite...
                        docker compose exec -T django python adria_project_backend/manage.py test tests
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
                body: "🎉 All containers are running and Django tests passed successfully.",
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
