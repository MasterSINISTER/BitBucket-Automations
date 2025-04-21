pipeline {
    agent any
   
    parameters {
        string(name: 'SOURCE_BRANCH', defaultValue: 'staging', description: 'Source branch to compare')
        string(name: 'DESTINATION_BRANCH', defaultValue: 'uat', description: 'Destination branch to compare against')
    }
   
    stages {
        stage('Run Branch Comparison') {
            steps {
                script {
                    // The script is now directly part of your repo
                    // No need for libraryResource
                   
                    // Run the Python script with environment variables and credentials
                    withCredentials([usernamePassword(credentialsId: 'bitbucket-credentials',
                                    usernameVariable: 'BITBUCKET_USERNAME',
                                    passwordVariable: 'BITBUCKET_PASSWORD')]) {
                        withEnv([
                            "SOURCE_BRANCH=${params.SOURCE_BRANCH}",
                            "DESTINATION_BRANCH=${params.DESTINATION_BRANCH}",
                            "WORKSPACE=smartscreen"
                        ]) {
                            bat '"C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" branch_comparison.py'
                        }
                    }
                }
            }
        }
       
        // Rest of your pipeline remains the same
        // ...
    }

    
    post {
        success {
            echo "Successfully completed branch comparison scan!"
        }
        failure {
            echo "Branch comparison scan failed!"
        }
    }
}