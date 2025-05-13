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
                // Report that build is in progress
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis'
                )
                
                withSonarQubeEnv('SonarQube') {
                    script {
                        // Get branch/PR info from Bitbucket variables if available
                        def isPR = env.BITBUCKET_PR_ID ? true : false
                        def branchName = env.BITBUCKET_BRANCH ?: env.GIT_BRANCH
                        
                        if (isPR) {
                            // PR analysis
                            bat """
                            sonar-scanner.bat \
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.pullrequest.key=${env.BITBUCKET_PR_ID} \
                              -Dsonar.pullrequest.branch=${env.BITBUCKET_BRANCH} \
                              -Dsonar.pullrequest.base=${env.BITBUCKET_TARGET_BRANCH}
                            """
                        } else {
                            // Branch analysis
                            bat """
                            sonar-scanner.bat \
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.branch.name=${branchName}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    // Wait for quality gate result
                    timeout(time: 5, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            // Quality gate failed - fail the build
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
