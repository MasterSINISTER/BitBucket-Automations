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
                    // Create the Python script for branch comparison
                    writeFile file: 'branch_comparison.py', text: libraryResource('branch_comparison.py')
                    
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
        
        stage('Generate Report') {
            steps {
                script {
                    // Read the summary file and set it as the build description
                    if (fileExists('branch_comparison_summary.txt')) {
                        def summary = readFile('branch_comparison_summary.txt')
                        currentBuild.description = summary
                    }
                    
                    // Archive the outputs
                    archiveArtifacts artifacts: 'branch_comparison_*.txt', allowEmptyArchive: true
                }
            }
        }
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