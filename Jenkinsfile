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
                   withCredentials([usernamePassword(
                        credentialsId: 'c8fdd3a7-6739-4422-af2c-5d305f59f44d',
                        usernameVariable: 'BITBUCKET_USERNAME',
                        passwordVariable: 'BITBUCKET_PASSWORD')])
                    {
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
    always {
        script {
            if (fileExists('branch_comparison_summary.txt')) {
                def summaryContent = readFile 'branch_comparison_summary.txt'
                
                // Using credentials for email if needed
                withCredentials([usernamePassword(
                    credentialsId: '19cd0085-82f4-4eb9-acb8-5bf84f4e2324', 
                    usernameVariable: 'EMAIL_USERNAME', 
                    passwordVariable: 'EMAIL_PASSWORD')]) {
                    
                    emailext(
                        to: 'rishabhgupta200230@gmail.com',
                        subject: "Bitbucket Branch Comparison: ${params.SOURCE_BRANCH} → ${params.DESTINATION_BRANCH}",
                        body: """
                        <h2>Branch Comparison Summary</h2>
                        <p>Source Branch: ${params.SOURCE_BRANCH}</p>
                        <p>Destination Branch: ${params.DESTINATION_BRANCH}</p>
                        <pre>${summaryContent}</pre>
                        """,
                        mimeType: 'text/html',
                    )
                }
                echo "Email sent with branch comparison summary."
            } else {
                echo "Summary file not found. Email not sent."
                error "Summary file 'branch_comparison_summary.txt' was not generated."
            }
        }
    }
}
}