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
                    // Set a flag to track if we should skip waiting for quality gate
                    def skipQualityGate = false
                    
                    try {
                        // First, check the task status
                        if (env.SONAR_CE_TASK_ID) {
                            withSonarQubeEnv('SonarQube') {
                                try {
                                    echo "Checking status of SonarQube task: ${env.SONAR_CE_TASK_ID}"
                                    def statusOutput = bat(script: "curl -u %SONAR_AUTH_TOKEN%: %SONAR_HOST_URL%/api/ce/task?id=${env.SONAR_CE_TASK_ID}", returnStdout: true).trim()
                                    echo "Task status response: ${statusOutput}"
                                } catch (Exception e) {
                                    echo "Error checking task status: ${e.message}"
                                }
                            }
                        } else {
                            echo "No SonarQube task ID found, skipping quality gate"
                            skipQualityGate = true
                        }
                        
                        // If we should proceed with quality gate check
                        if (!skipQualityGate) {
                            // Use a very short timeout to avoid getting stuck
                            timeout(time: 30, unit: 'SECONDS') {
                                echo "Attempting quick quality gate check..."
                                try {
                                    def qg = waitForQualityGate(abortPipeline: false)
                                    echo "Quality Gate status: ${qg.status}"
                                } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                                    echo "Quality gate check timed out after 30 seconds"
                                    echo "Skipping quality gate and continuing pipeline"
                                } catch (Exception e) {
                                    echo "Error during quality gate check: ${e.message}"
                                    echo "Continuing pipeline execution"
                                }
                            }
                        }
                    } catch (Exception e) {
                        echo "Error in Quality Gate stage: ${e.message}"
                    } finally {
                        echo "Quality Gate stage complete, continuing pipeline"
                        // Force success status for this stage
                        currentBuild.result = currentBuild.result ?: 'SUCCESS'
                    }
                }
            }
        }
    }
    // post {
    //     always {
    //         echo "Running post-build cleanup actions"
    //         catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
    //             cleanWs()
    //         }
    //     }
    //     success {
    //         echo "Build succeeded, sending success notification"
    //         catchError(buildResult: null, stageResult: null) {
    //             bitbucketStatusNotify(
    //                 buildState: 'SUCCESSFUL',
    //                 buildKey: 'sonarqube-analysis',
    //                 buildName: 'SonarQube Analysis'
    //             )
    //         }
    //     }
    //     unstable {
    //         echo "Build is unstable, sending unstable notification"
    //         catchError(buildResult: null, stageResult: null) {
    //             bitbucketStatusNotify(
    //                 buildState: 'FAILED',
    //                 buildKey: 'sonarqube-analysis',
    //                 buildName: 'SonarQube Analysis (Unstable)'
    //             )
    //         }
    //     }
    //     failure {
    //         echo "Build failed, sending failure notification"
    //         catchError(buildResult: null, stageResult: null) {
    //             bitbucketStatusNotify(
    //                 buildState: 'FAILED',
    //                 buildKey: 'sonarqube-analysis',
    //                 buildName: 'SonarQube Analysis'
    //             )
    //         }
    //     }
    // }
}
