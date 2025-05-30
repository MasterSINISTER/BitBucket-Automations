pipeline {
    agent any

    parameters {
        booleanParam(name: 'DRY_RUN', defaultValue: true, description: 'Dry run without deleting branches')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Branch Cleanup') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'bitbucket-creds-id', usernameVariable: 'USERNAME', passwordVariable: 'APP_PASSWORD')]) {
                    script {
                        def dryRunFlag = params.DRY_RUN ? "True" : "False"
                        bat """
                            set BITBUCKET_USERNAME=%USERNAME%
                            set BITBUCKET_APP_PASSWORD=%APP_PASSWORD%
                            "C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" branch_comparison.py ${dryRunFlag}
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo '✅ Branch cleanup completed.'
        }
    }
}
