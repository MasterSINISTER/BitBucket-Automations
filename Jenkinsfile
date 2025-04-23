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
                def fullSummary = readFile 'branch_comparison_summary.txt'
                def summaryLines = []
                def foundSummary = false
                def lineCount = 0
                
                // Process the file line by line
                fullSummary.split('\n').each { line ->
                    if (line.trim() == 'SUMMARY') {
                        foundSummary = true
                        summaryLines.add(line)
                    } else if (foundSummary && lineCount < 1) { // Just get the first line after SUMMARY
                        summaryLines.add(line)
                        lineCount++
                    }
                }
                
                // Join the extracted lines
                def extractedSummary = summaryLines.join('\n')
                
                // Send only the extracted summary lines
                emailext(
                    to: 'rishabhgupta200230@gmail.com',
                    subject: "Bitbucket Branch Comparison: ${params.SOURCE_BRANCH} → ${params.DESTINATION_BRANCH}",
                    body: """
                    <h2>Branch Comparison Summary</h2>
                    <p>Source Branch: ${params.SOURCE_BRANCH}</p>
                    <p>Destination Branch: ${params.DESTINATION_BRANCH}</p>
                    <pre>${extractedSummary}</pre>
                    """,
                    mimeType: 'text/html'
                )
                echo "Email sent with extracted summary information."
            } else {
                echo "Summary file not found. Email not sent."
                error "Summary file 'branch_comparison_summary.txt' was not generated."
            }
        }
    }
}
}