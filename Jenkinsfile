pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = "dockerautopilot"
        SCANNER_HOME = tool 'sonar-scanner'
        SONARQUBE_ENV = "sonar-scanner"
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
    }

    post {
        always {
            script {
                currentBuild.result = currentBuild.result ?: 'SUCCESS'
                notifyBitbucket()
            }
        }

        failure {
            script {
                notifyBitbucket()
            }
        }
    }
}
