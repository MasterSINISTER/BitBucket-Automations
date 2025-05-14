pipeline {
    agent any
    environment {
        SONAR_PROJECT_KEY = "dockerautopilot"
        SONARQUBE_ENV = "sonar-scanner"
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Use checkout scm to get code and repository information
                checkout scm
                
                // Capture git commit information for Bitbucket notification
                script {
                    // Extract repository details from the checkout
                    env.GIT_COMMIT = bat(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.GIT_BRANCH = bat(script: 'git name-rev --name-only HEAD', returnStdout: true).trim()
                    
                    // Extract repository URL
                    def repositoryUrl = bat(script: 'git config --get remote.origin.url', returnStdout: true).trim()
                    
                    // Parse repository name and owner from URL
                    // This handles both HTTPS and SSH URLs from Bitbucket
                    if (repositoryUrl.contains('bitbucket.org')) {
                        def matcher
                        if (repositoryUrl.startsWith('https://')) {
                            // Format: https://bitbucket.org/owner/repo.git
                            matcher = repositoryUrl =~ /https:\/\/.*bitbucket\.org\/([^\/]+)\/([^\/\.]+)(\.git)?/
                        } else {
                            // Format: git@bitbucket.org:owner/repo.git
                            matcher = repositoryUrl =~ /git@bitbucket\.org:([^\/]+)\/([^\/\.]+)(\.git)?/
                        }
                        
                        if (matcher.matches()) {
                            env.GIT_REPO_OWNER = matcher[0][1]
                            env.GIT_REPO_NAME = matcher[0][2]
                            echo "Repository: ${env.GIT_REPO_OWNER}/${env.GIT_REPO_NAME}"
                        } else {
                            echo "Warning: Could not parse repository information from URL: ${repositoryUrl}"
                            // Fallback method if needed
                            def parts = repositoryUrl.tokenize('/')
                            env.GIT_REPO_NAME = parts.last().replace('.git', '')
                        }
                    }
                }
                
                // Notify Bitbucket that build is starting
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis'
                )
            }
        }
        
        stage('SonarQube analysis') {
            steps {
                // Notify Bitbucket that SonarQube analysis is starting
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'sonar-scan',
                    buildName: 'Running SonarQube Scan'
                )
                
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    bat """
                        ${SONARQUBE_ENV}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/*.html,values.yaml \
                        -Dsonar.python.version=3.8
                    """
                }
                
                // Notify Bitbucket that SonarQube analysis completed
                bitbucketStatusNotify(
                    buildState: 'SUCCESSFUL',
                    buildKey: 'sonar-scan',
                    buildName: 'SonarQube Scan Complete'
                )
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // Notify Bitbucket that quality gate check is starting
                bitbucketStatusNotify(
                    buildState: 'INPROGRESS',
                    buildKey: 'quality-gate',
                    buildName: 'SonarQube Quality Gate'
                )
                
                script {
                    try {
                        def qg = waitForQualityGate()
                        env.QUALITY_GATE_STATUS = qg.status
                        
                        if (qg.status != 'OK') {
                            // Quality gate failed - notify Bitbucket and fail the build
                            bitbucketStatusNotify(
                                buildState: 'FAILED',
                                buildKey: 'quality-gate',
                                buildName: 'SonarQube Quality Gate',
                                buildDescription: "Quality Gate status: ${qg.status}"
                            )
                            
                            currentBuild.result = 'FAILURE'
                            error "SonarQube Quality Gate failed: ${qg.status}"
                        } else {
                            // Quality gate passed - notify Bitbucket
                            bitbucketStatusNotify(
                                buildState: 'SUCCESSFUL',
                                buildKey: 'quality-gate',
                                buildName: 'SonarQube Quality Gate',
                                buildDescription: "Quality Gate status: ${qg.status}"
                            )
                        }
                    } catch (Exception e) {
                        // In case of any other errors
                        bitbucketStatusNotify(
                            buildState: 'FAILED',
                            buildKey: 'quality-gate',
                            buildName: 'SonarQube Quality Gate',
                            buildDescription: "Error: ${e.message}"
                        )
                        throw e
                    }
                }
            }
        }
    }
    
    post {
        success {
            bitbucketStatusNotify(
                buildState: 'SUCCESSFUL',
                buildDescription: "Build completed successfully"
            )
        }
        failure {
            bitbucketStatusNotify(
                buildState: 'FAILED',
                buildDescription: "Build failed"
            )
        }
        aborted {
            bitbucketStatusNotify(
                buildState: 'FAILED',
                buildDescription: "Build was aborted"
            )
        }
    }
}
