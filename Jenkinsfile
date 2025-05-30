pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install requests'
            }
        }

        stage('Run Branch Cleanup') {
            environment {
                BITBUCKET_USERNAME = credentials('d68eb646-f561-4194-a5be-a369c2f86120')       // Secret Text
                BITBUCKET_APP_PASSWORD = credentials('d68eb646-f561-4194-a5be-a369c2f86120') // Secret Text
            }
            steps {
                bat """
                echo Running Bitbucket branch cleanup...
                echo Username: %BITBUCKET_USERNAME%
                %PYTHON% branch_cleanup.py
                """
            }
        }
    }
}

