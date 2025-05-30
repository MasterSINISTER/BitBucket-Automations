pipeline {
    agent any

    environment {
        USERNAME = credentials('bitbucket-username')
        APP_PASSWORD = credentials('bitbucket-app-password')
        PYTHON_PATH = 'C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    stages {
        stage('Run Branch Cleanup') {
            steps {
                bat """
                echo Python Version:
                %PYTHON_PATH% --version

                echo Running Branch Cleanup Script...
                %PYTHON_PATH% branch_cleanup.py
                """
            }
        }
    }
}
