pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'docker-compose build'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                docker-compose up -d
                sh 'make check || true'
                junit '**/target/*.xml'
            }
        }
        stage('QA') {
            steps {
                echo 'Testing..'
                make codacy-report
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }

}
