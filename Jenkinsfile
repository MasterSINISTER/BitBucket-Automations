pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = "adv-app"
        BITBUCKET_CREDS = credentials('c8fdd3a7-6739-4422-af2c-5d305f59f44d')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    def originUrl = bat(script: 'git remote get-url origin', returnStdout: true).trim()
                    def slug = originUrl
                        .replaceFirst(/.*bitbucket\.org[:\/]/, '') // works for both ssh and https
                        .replaceFirst(/\.git$/, '')
                    env.REPO_SLUG = slug
                    echo "Repo slug: ${env.REPO_SLUG}"
                }

            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    bitbucketStatusNotify(
                        buildState: 'INPROGRESS',
                        buildKey: 'sonarqube-analysis',
                        buildName: 'SonarQube Analysis',
                        repoSlug: env.REPO_SLUG,
                        commitId: env.GIT_COMMIT
                    )
                }

                withSonarQubeEnv('SonarQube') {
                    script {
                        def sonarParams = "-Dsonar.projectKey=${SONAR_PROJECT_KEY} " +
                                          "-Dsonar.projectName=${SONAR_PROJECT_KEY} " +
                                          "-Dsonar.scm.provider=git " +
                                          "-Dsonar.sources=."

                        bat "sonar-scanner ${sonarParams}"

                        try {
                            def taskId = null
                            if (fileExists('.scannerwork/report-task.txt')) {
                                def props = readProperties(file: '.scannerwork/report-task.txt')
                                taskId = props['ceTaskId']
                                env.SONAR_CE_TASK_ID = taskId
                                echo "SonarQube task ID: ${taskId}"
                            } else {
                                echo "Report task file not found"
                            }
                        } catch (Exception e) {
                            echo "Could not extract task ID: ${e.message}"
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    try {
                        timeout(time: 1, unit: 'MINUTES') {
                            def qg = env.SONAR_CE_TASK_ID ?
                                (waitForQualityGate(taskId: env.SONAR_CE_TASK_ID)) :
                                 waitForQualityGate()

                            if (qg.status != 'OK') {
                                currentBuild.result = 'FAILURE'
                                error "Quality Gate failed: ${qg.status}"
                            }
                        }
                    } catch (Exception e) {
                        echo "Quality Gate check failed: ${e.message}"
                        echo "Continuing pipeline despite Quality Gate issues"
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            script {
                bitbucketStatusNotify(
                    buildState: 'SUCCESSFUL',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis',
                    repoSlug: env.REPO_SLUG,
                    commitId: env.GIT_COMMIT
                )
            }
        }
        failure {
            script {
                bitbucketStatusNotify(
                    buildState: 'FAILED',
                    buildKey: 'sonarqube-analysis',
                    buildName: 'SonarQube Analysis',
                    repoSlug: env.REPO_SLUG,
                    commitId: env.GIT_COMMIT
                )
            }
        }
    }
}
