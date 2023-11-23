pipeline {
    agent {
        label 'Sandbox_6G'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    
    //environment {
    //    REPO_URL = 'https://github.com/alvarocurt/TNLCM'
    //}

    stages {

        stage('Clone Repositories') {
            steps {
                //git branch: 'main', url: "${REPO_URL}"
                checkout scm
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
