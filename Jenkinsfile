// pipeline {
//     agent any

//     parameters {
//         string(name: 'SOURCE_BRANCH', defaultValue: 'staging', description: 'Source branch to compare')
//         string(name: 'DESTINATION_BRANCH', defaultValue: 'uat', description: 'Destination branch to compare against')
//     }

// stages ('IP Whitelist'){
// stage('Run Branch Comparison') {
//     agent any
//     steps {
//         script {
//             withCredentials([usernamePassword(
//                 credentialsId: 'bitbucket-repo-read-app-password', 
//                 usernameVariable: 'BITBUCKET_USERNAME', 
//                 passwordVariable: 'BITBUCKET_PASSWORD')]) 
//                 {

//                 withEnv([
//                     "SOURCE_BRANCH=${params.SOURCE_BRANCH}",
//                     "DESTINATION_BRANCH=${params.DESTINATION_BRANCH}",
//                     "WORKSPACE=smartscreen"
//                 ]) {
//                         bat '"C:\\Users\\MasterSINISTER\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" branch_comparison.py'
//                 }
//             }
//         }
//     }
// }


// }
//    post {
//         success {
//             echo "Successfully completed pipeline!"
//         }
//         failure {
//             echo "Pipeline failed!"
//         }
//     }
// }





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
    success {
        script {
            def fullSummary = readFile 'branch_comparison_summary.txt'
            def changesOnly = ''
            def lines = fullSummary.readLines()
            def inChanges = false

            lines.each { line ->
                if (line.trim() == 'REPOSITORIES WITH CHANGES') {
                    inChanges = true
                    changesOnly += line + '\n'
                    return
                }
                if (inChanges && (line.trim() == '' || line.contains('REPOSITORIES WITH'))) {
                    inChanges = false
                }
                if (inChanges) {
                    changesOnly += line + '\n'
                }
            }

            if (changesOnly.trim()) {
                emailext(
                    to: 'hellolucifer007@gmail.com',
                    subject: "🔔 Bitbucket Changes Detected",
                    body: """Repositories with changes:\n\n${changesOnly.trim()}"""
                )
            } else {
                echo "No changes found, email not sent."
            }
        }
    }
}

}

