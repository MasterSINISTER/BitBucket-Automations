pipeline {
    options {
        ansiColor('xterm')
    }

    agent { 
        label 'DEVBOX' 
    }

    environment {
        SONAR_PROJECT_KEY = "dockerautopilot"
        SCANNER_HOME = tool 'sonar-scanner'
        SONARQUBE_ENV = "sonar-scanner"
        BITBUCKET_CRED_ID = "bitbucket-repo-read-app-password"
        BITBUCKET_USERNAME = credentials("bitbucket-repo-read-app-password")
        BITBUCKET_APP_PASSWORD = credentials("bitbucket-repo-read-app-password")
        REPO_SLUG = "dockerautopilot"
        WORKSPACE = "smartscreen"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh """
                        ${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/*.html,values.yaml \
                        -Dsonar.python.version=3.8
                    """
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                script {
                    def qg = waitForQualityGate()
                    env.QUALITY_GATE_STATUS = qg.status
                    if (qg.status != 'OK') {
                        error "SonarQube Quality Gate failed: ${qg.status}"
                    }
                }
            }
        }

        stage('Notify Bitbucket') {
            steps {
                script {
                    def state = (env.QUALITY_GATE_STATUS == 'OK') ? "SUCCESSFUL" : "FAILED"
                    def description = "SonarQube Quality Gate: ${env.QUALITY_GATE_STATUS}"
                    def buildKey = "SonarQube"
                    withCredentials([usernamePassword(credentialsId: 'bitbucket-repo-read-app-password', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh """
                            curl -X POST -u \$USERNAME:\$PASSWORD \\
                            https://api.bitbucket.org/2.0/repositories/${WORKSPACE}/${REPO_SLUG}/commit/${env.GIT_COMMIT}/statuses/build \\
                            -H 'Content-Type: application/json' \\
                            -d '{"state":"${state}","key":"${buildKey}","name":"SonarQube Quality Gate","url":"${env.BUILD_URL}","description":"${description}"}'
                       """
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
