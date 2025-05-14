pipeline {
    agent any
    environment {
        SONAR_PROJECT_KEY = "adv-app"
        BITBUCKET_CREDS = credentials('c8fdd3a7-6739-4422-af2c-5d305f59f44d')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis',
                )

                withSonarQubeEnv('SonarQube') {
                    script {
                        def sonarParams = "-Dsonar.projectKey=${SONAR_PROJECT_KEY} " +
                                          "-Dsonar.projectName=${SONAR_PROJECT_KEY} " +
                                          "-Dsonar.scm.provider=git " +
                                          "-Dsonar.sources=."

                        if (env.BITBUCKET_PR_ID) {
                            echo "Running analysis for PR ${env.BITBUCKET_PR_ID}"
                        }

                        bat "sonar-scanner ${sonarParams}"

                        try {
                            def taskId = null
                            if (fileExists('.scannerwork/report-task.txt')) {
                                def props = readProperties(file: '.scannerwork/report-task.txt')
                                taskId = props['ceTaskId']
                                env.SONAR_CE_TASK_ID = taskId
                                echo "SonarQube task ID: ${taskId}"
                            } else {
                                echo "Report task file not found"
                            }
                        } catch (Exception e) {
                            echo "Could not extract task ID: ${e.message}"
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    try {
                        timeout(time: 10, unit: 'MINUTES') {
                            def qg = env.SONAR_CE_TASK_ID ?
                                (waitForQualityGate(taskId: env.SONAR_CE_TASK_ID)) :
                                 waitForQualityGate()


                            if (qg.status != 'OK') {
                                currentBuild.result = 'FAILURE'
                                error "Quality Gate failed: ${qg.status}"
                            }
                        }
                    } catch (Exception e) {
                        echo "Quality Gate check failed: ${e.message}"
                        echo "Continuing pipeline despite Quality Gate issues"
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            bitbucketStatusNotify(
                buildState: 'SUCCESSFUL',
                buildKey: 'sonarqube-analysis',
                buildName: 'SonarQube Analysis',
            )
        }
        failure {
            bitbucketStatusNotify(
                buildState: 'FAILED',
                buildKey: 'sonarqube-analysis',
                buildName: 'SonarQube Analysis',
            )
        }
    }
}
