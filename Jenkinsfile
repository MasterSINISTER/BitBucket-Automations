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
                withCredentials([usernamePassword(credentialsId: 'd68eb646-f561-4194-a5be-a369c2f86120', usernameVariable: 'USERNAME', passwordVariable: 'APP_PASSWORD')]) {
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
            echo 'Branch cleanup completed.'
        }
    }
}
