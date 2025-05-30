pipeline {
    agent any

    environment {
        USERNAME = credentials('d68eb646-f561-4194-a5be-a369c2f86120')
        APP_PASSWORD = credentials('d68eb646-f561-4194-a5be-a369c2f86120')
        PYTHON_PATH = 'C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    stages {
        stage('Run Branch Cleanup') {
            steps {
                bat """
                echo Python Version:
                %PYTHON_PATH% --version

                echo Running Branch Cleanup Script...
                %PYTHON_PATH% branch_comparison.py
                """
            }
        }
    }
}
