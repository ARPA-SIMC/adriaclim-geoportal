pipeline {
    agent any

    // parameters {
    
    //     string(name: 'MAIL_RECIPIENTS', defaultValue: 'you@example.com', description: 'Email recipients for notifications')
    //     booleanParam(name: 'DOCKER_PRUNE', defaultValue: false, description: 'Run docker system prune -af before build?')
    // }

    environment {
        PROJECT_ROOT = 'adriaclim-master'
        BACKEND_SERVICE = 'django'
        HEALTHCHECK_URL = 'http://localhost:8000'
    }

    stages {

        // stage('Checkout') {
        //     steps {
        //         echo "Checking out the repository..."
        //         checkout scm
        //     }
        // }

        stage('Cleanup Environment') {
                    steps {
                        dir("${PROJECT_ROOT}") {
                            bat '''
                                echo Cleaning up containers, volumes and orphans
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

        stage('Build & Start Containers') {
            steps {
                dir("${PROJECT_ROOT}") {
                    bat '''
                        echo Building and starting all containers
                        docker compose up -d --build
                        echo Showing running containers...
                        docker compose ps
                    '''
                }
            }
        }

        // stage('Wait for Migrator') {
        //     steps {
        //         script {
        //             echo "Waiting for migrator container (adriapp_migrator) to finish..."
        //             while (true) {
        //                 // Controllo se il container esiste
        //                 def exists = bat(returnStatus: true, script: "docker inspect adriapp_migrator >NUL 2>&1")
        //                 if (exists != 0) {
        //                     echo "Migrator container not found yet, waiting 5s..."
        //                     sleep(time: 5, unit: 'SECONDS')
        //                     continue
        //                 }

        //                 // Se esiste, controllo se sta ancora girando
        //                 def running = bat(returnStdout: true, script: "docker inspect -f \"{{.State.Running}}\" adriapp_migrator").trim()

        //                 if (running == "false") {
        //                     // exit code
        //                     def exitCode = bat(returnStdout: true, script: "docker inspect -f \"{{.State.ExitCode}}\" adriapp_migrator").trim()
        //                     if (exitCode == "0") {
        //                         echo "Migrator finished successfully."
        //                         break
        //                     } else {
        //                         error("Migrator container exited with error code ${exitCode}")
        //                     }
        //                 } else {
        //                     echo "Migrator still running, waiting 10s..."
        //                     sleep(time: 10, unit: 'SECONDS')
        //                 }
        //             }
        //         }
        //     }
        // }

        // stage('Wait for Django Healthcheck') {
        //     steps {
        //         script {
        //             def maxRetries = 30
        //             def started = false

        //             for (int i = 1; i <= maxRetries; i++) {
        //                 echo "Healthcheck attempt ${i}/${maxRetries}..."

        //                 def httpCode = bat(
        //                     returnStdout: true,
        //                     script: "curl -s -o NUL -w %%{http_code} ${HEALTHCHECK_URL}"
        //                 ).trim()

        //                 if (httpCode == "200") {
        //                     echo "Django is healthy!"
        //                     started = true
        //                     break
        //                 } else {
        //                     echo "Django not ready yet (HTTP ${httpCode}), waiting 10 seconds..."
        //                     sleep(time: 10, unit: 'SECONDS')
        //                 }
        //             }

        //             if (!started) {
        //                 error("Django did NOT become healthy within 5 minutes.")
        //             }
        //         }
        //     }
        // }

//         stage('Verify Containers Status') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     echo "Checking container status..."
//                     bat 'docker compose ps'
//                 }
//             }
//         }

//         stage('Run Django Tests') {
//             steps {
//                 dir("${PROJECT_ROOT}") {
//                     bat '''
//                         echo Running Django test suite...
//                         docker compose exec -T django python adria_project_backend/manage.py test tests
//                     '''
//                 }
//             }
//         }
//     }

//     post {
//         success {
//             echo 'Pipeline completed successfully.'
//             emailext (
//                 subject: "SUCCESS: Jenkins pipeline completed",
//                 body: "All containers are running and Django tests passed successfully.",
//                 to: "${params.MAIL_RECIPIENTS}"
//             )
//         }
//         failure {
//             echo 'Pipeline failed.'
//             emailext (
//                 subject: "FAILURE: Jenkins pipeline failed",
//                 body: "One or more stages failed. Please check Jenkins logs for details.",
//                 to: "${params.MAIL_RECIPIENTS}"
//             )
//         }
//         always {
//             echo 'Final cleanup: stopping containers...'
//             dir("${PROJECT_ROOT}") {
//                 bat 'docker compose down || echo "Ignoring errors in final docker down"'
//             }
//         }
    }
}
