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
                def extractedLines = []
                def capture = false

                fullSummary.split('\n').each { line ->
                    if (line.startsWith("Repositories with changes:")) {
                        capture = true
                        extractedLines.add(line)
                    } else if (capture) {
                        if (line.startsWith("Repositories")) {
                            capture = false // Stop if another section begins
                        } else if (line.trim()) {
                            extractedLines.add(line)
                        }
                    }
                }

                def extractedSummary = extractedLines.join('\n')

                emailext(
                    to: 'rishabhgupta200230@gmail.com',
                    subject: "Bitbucket Branch Comparison: ${params.SOURCE_BRANCH} → ${params.DESTINATION_BRANCH}",
                    body: """
                    <h2>Repositories with Changes</h2>
                    <p>Source Branch: ${params.SOURCE_BRANCH}</p>
                    <p>Destination Branch: ${params.DESTINATION_BRANCH}</p>
                    <pre>${extractedSummary}</pre>
                    """,
                    mimeType: 'text/html'
                )
                echo "Email sent with filtered repository change summary."
            } else {
                echo "Summary file not found. Email not sent."
                error "Summary file 'branch_comparison_summary.txt' was not generated."
            }
        }
    }
}

}