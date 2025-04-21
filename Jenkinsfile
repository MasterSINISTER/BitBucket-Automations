pipeline {
    agent {
            label 'DEVBOX'
          }
   options {
    ansiColor('xterm')
  }
    parameters {
        string(name: 'SOURCE_BRANCH', defaultValue: 'staging', description: 'Source branch to compare')
        string(name: 'DESTINATION_BRANCH', defaultValue: 'uat', description: 'Destination branch to compare against')
    }

stages ('IP Whitelist'){
stage('Run Branch Comparison') {
    agent any
    steps {
        script {
            withCredentials([usernamePassword(
                credentialsId: 'bitbucket-repo-read-app-password', 
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


}
   post {
        success {
            echo "Successfully completed pipeline!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
