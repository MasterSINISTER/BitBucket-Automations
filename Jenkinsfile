pipeline {
    agent any
    
    environment {
        SONAR_PROJECT_KEY = "dockerautopilot"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                // Notify Bitbucket that analysis is starting
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis'
                )
                
                withSonarQubeEnv('SonarQube') {
                    script {
                        // Initialize basic parameters
                        def sonarParams = "-Dsonar.projectKey=${SONAR_PROJECT_KEY}"
                        
                        // Additional parameters if we have PR info (works in Community Edition)
                        if (env.BITBUCKET_PR_ID) {
                            echo "Running analysis for PR ${env.BITBUCKET_PR_ID}"
                            // Note: CE doesn't support -Dsonar.pullrequest.* but we can still analyze the code
                        }
                        
                        // Run the scanner with appropriate parameters
                        bat "sonar-scanner.bat ${sonarParams}"
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            currentBuild.result = 'FAILURE'
                            error "Quality Gate failed: ${qg.status}"
                        }
                    }
                }
            }
        }
    }
    
    post {
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
