pipeline {
    agent {
        label 'Sandbox_6G'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    
    environment {
        REPO_URL = 'https://github.com/alvarocurt/TNLCM'
    }

    stages {

        stage ('Clean Workspace') {
            steps {
                docker compose down
                deleteDir() /* clean up our workspace */
            }
        }

        stage('Clone Repositories') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
                // checkout scm may work too
            }
        }


        stage('Delete previous containers if any') {
            steps {
                script {
                    sh "docker compose down || true"
                }
            }
        }

        stage('Build docker compose') {
            steps {
                script {
                    dir('subDir') {
                        sh 'docker compose up -d'
                    }
                }
            }
        }
    }
}
