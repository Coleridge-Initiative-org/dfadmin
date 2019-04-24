pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'docker-compose build'
                sh 'make git-submodules-init'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                sh 'docker-compose up -d'
                sh 'make check || true'
                junit '**/target/*.xml'
            }
        }
        stage('QA') {
            steps {
                echo 'Testing..'
                sh 'make codacy-report'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }

}
