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
                        timeout(time: 3, unit: 'MINUTES') {  // Reduced timeout to avoid long waits
                            echo "Waiting for SonarQube task ID: ${env.SONAR_CE_TASK_ID}"
                            
                            // Check task status first
                            if (env.SONAR_CE_TASK_ID) {
                                withSonarQubeEnv('SonarQube') {
                                    def statusOutput = bat(script: "curl -u %SONAR_AUTH_TOKEN%: %SONAR_HOST_URL%/api/ce/task?id=${env.SONAR_CE_TASK_ID}", returnStdout: true).trim()
                                    echo "Current task status: ${statusOutput}"
                                }
                            }
                            
                            // Instead of waiting indefinitely, set a shorter timeout for waitForQualityGate
                            echo "Checking quality gate with timeout..."
                            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                                def qg = waitForQualityGate(abortPipeline: false)
                                echo "Quality Gate status: ${qg.status}"
                                
                                if (qg.status != 'OK') {
                                    currentBuild.result = 'UNSTABLE'
                                    echo "Quality Gate failed with status: ${qg.status}"
                                }
                            }
                        }
                    } catch (Exception e) {
                        // Just log the exception and continue
                        echo "Quality Gate check failed: ${e.message}"
                        echo "Error details: ${e.toString()}"
                        echo "Continuing pipeline despite Quality Gate issues"
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Always send a status notification
                        echo "Quality Gate stage finished, moving to post actions"
                    }
                }
            }
            post {
                always {
                    echo "Inside Quality Gate stage post actions"
                }
            }
        }
            }
        }
    }
    post {
        always {
            echo "Running post-build cleanup actions"
            catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                cleanWs()
            }
        }
        success {
            echo "Build succeeded, sending success notification"
            catchError(buildResult: null, stageResult: null) {
                bitbucketStatusNotify(
                    buildState: 'SUCCESSFUL',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis'
                )
            }
        }
        unstable {
            echo "Build is unstable, sending unstable notification"
            catchError(buildResult: null, stageResult: null) {
                bitbucketStatusNotify(
                    buildState: 'FAILED',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis (Unstable)'
                )
            }
        }
        failure {
            echo "Build failed, sending failure notification"
            catchError(buildResult: null, stageResult: null) {
                bitbucketStatusNotify(
                    buildState: 'FAILED',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis'
                )
            }
        }
    }
}
