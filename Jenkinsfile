pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = "adv-app"
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
                    buildName: 'SonarQube Analysis'
                )

                withSonarQubeEnv('SonarQube') {
                    script {
                        def sonarParams = "-Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.projectName=${SONAR_PROJECT_KEY} -Dsonar.sources=."

                        if (env.BITBUCKET_PR_ID) {
                            echo "Running analysis for PR ${env.BITBUCKET_PR_ID}"
                        }

                        bat "sonar-scanner.bat ${sonarParams}"

                        try {
                            def taskId = null
                            if (fileExists('.scannerwork\\report-task.txt')) {
                                def props = readFile('.scannerwork\\report-task.txt').split('\n').collectEntries {
                                    def parts = it.split('=')
                                    [(parts[0].trim()): parts[1].trim()]
                                }
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
                timeout(time: 10, unit: 'MINUTES') {  // Increased timeout
                    echo "Waiting for SonarQube quality gate with task ID: ${env.SONAR_CE_TASK_ID}"
                    
                    // Try checking task status directly first
                    if (env.SONAR_CE_TASK_ID) {
                        withSonarQubeEnv('SonarQube') {
                            bat "curl -u ${SONAR_AUTH_TOKEN}: ${SONAR_HOST_URL}/api/ce/task?id=${env.SONAR_CE_TASK_ID}"
                        }
                    }
                    
                    def qg = env.SONAR_CE_TASK_ID ?
                        waitForQualityGate(taskId: env.SONAR_CE_TASK_ID, abortPipeline: false) :
                        waitForQualityGate(abortPipeline: false)
                        
                    echo "Quality Gate status: ${qg.status}"
                    
                    if (qg.status != 'OK') {
                        currentBuild.result = 'UNSTABLE'
                        echo "Quality Gate failed with status: ${qg.status}"
                    }
                }
            } catch (Exception e) {
                echo "Quality Gate check failed: ${e.message}"
                echo "Continuing pipeline despite Quality Gate issues"
                currentBuild.result = 'UNSTABLE'
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
                buildName: 'SonarQube Analysis'
            )
        }
        failure {
            bitbucketStatusNotify(
                buildState: 'FAILED',
                buildKey: 'sonarqube-analysis',
                buildName: 'SonarQube Analysis'
            )
        }
    }
}
