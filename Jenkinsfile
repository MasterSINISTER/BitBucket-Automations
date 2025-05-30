pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    parameters {
        booleanParam(name: 'DRY_RUN', defaultValue: true, description: 'Dry run without deleting branches')
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout source code (make sure branch_cleanup.py is in repo)
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'bitbucket-creds-id', passwordVariable: 'APP_PASSWORD', usernameVariable: 'USERNAME')]) {
                    bat """
                        echo Username: %USERNAME%
                        echo Setting env vars...

                        setx BITBUCKET_USERNAME "%USERNAME%" /M
                        setx BITBUCKET_APP_PASSWORD "%APP_PASSWORD%" /M
                    """
                }
            }
        }

        stage('Run Branch Cleanup Script') {
            steps {
                script {
                    def dryRunFlag = params.DRY_RUN ? "True" : "False"
                    bat "${env.PYTHON} branch_cleanup.py ${dryRunFlag}"
                }
            }
        }
    }

    post {
        always {
            echo "✅ Job Completed. Check logs above for summary."
        }
    }
}
