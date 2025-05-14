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
                        timeout(time: 15, unit: 'MINUTES') {  // Extended timeout
                            echo "Waiting for SonarQube task ID: ${env.SONAR_CE_TASK_ID}"
                            
                            // Actively monitor task status before waiting for quality gate
                            if (env.SONAR_CE_TASK_ID) {
                                withSonarQubeEnv('SonarQube') {
                                    // Check task status first to verify it's running
                                    bat "curl -u %SONAR_AUTH_TOKEN%: %SONAR_HOST_URL%/api/ce/task?id=${env.SONAR_CE_TASK_ID}"
                                    
                                    // Poll for task completion before quality gate check
                                    def taskCompleted = false
                                    def maxAttempts = 10
                                    def attemptCount = 0
                                    
                                    while (!taskCompleted && attemptCount < maxAttempts) {
                                        attemptCount++
                                        echo "Polling SonarQube task status (attempt ${attemptCount}/${maxAttempts})..."
                                        
                                        // Use bat with curl for Windows compatibility
                                        def statusOutput = bat(script: "curl -u %SONAR_AUTH_TOKEN%: %SONAR_HOST_URL%/api/ce/task?id=${env.SONAR_CE_TASK_ID}", returnStdout: true).trim()
                                        echo "Status output: ${statusOutput}"
                                        
                                        // Check if task is complete
                                        if (statusOutput.contains('"status":"SUCCESS"') || statusOutput.contains('"status":"FAILED"')) {
                                            taskCompleted = true
                                            echo "SonarQube task processing completed"
                                        } else {
                                            echo "SonarQube task still processing, waiting 30 seconds..."
                                            sleep(time: 30, unit: 'SECONDS')
                                        }
                                    }
                                    
                                    // If we've completed all attempts and task is still not done
                                    if (!taskCompleted) {
                                        echo "Warning: SonarQube task did not complete in expected time"
                                    }
                                }
                            }
                            
                            echo "Proceeding to Quality Gate check..."
                            
                            // Try using a short timeout for the quality gate itself
                            timeout(time: 2, unit: 'MINUTES') {
                                // Wait for quality gate with updated syntax
                                def qg = waitForQualityGate(abortPipeline: false)
                                echo "Quality Gate status: ${qg.status}"
                                
                                if (qg.status != 'OK') {
                                    currentBuild.result = 'UNSTABLE'
                                    echo "Quality Gate failed with status: ${qg.status}"
                                }
                            }
                        }
                    } catch (Exception e) {
                        echo "Quality Gate check failed: ${e.message}"
                        echo "Error details: ${e.toString()}"
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
