pipeline {
    agent any

    environment {
        IMAGE_NAME = '441870321480.dkr.ecr.us-east-1.amazonaws.com/dfadmin'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Prepare') {
            steps {
                echo 'Initializing submodules..'
                sh 'ln -s local.env .env'
                sh 'git submodule update --init --recursive'
            }
        }
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'docker-compose build'
            }
        }
//        stage('Test') {
//            steps {
//                echo 'Testing..'
//                sh 'docker-compose up -d'
//               sh 'make check || true'
//                junit '**/target/*.xml'
//            }
//        }
//        stage('Stopping') {
//            steps {
//                echo 'Stopping DFAdmin..'
//                sh 'docker-compose stop'
//            }
//        }
//        stage('QA') {
//            steps {
//                echo 'Testing..'
//                sh 'make codacy-report'
//            }
//        }
        stage('Scan') {
            steps {
//                sh 'apk add bash curl'
//                sh 'curl -s https://ci-tools.anchore.io/inline_scan-v0.3.3 | bash -s -- -d Dockerfile -b .anchore_policy.json ${IMAGE_NAME}:ci'
                sh 'curl -s https://ci-tools.anchore.io/inline_scan-v0.3.3 | bash -s -- ${IMAGE_NAME}:ci'
            }
        }
        stage('Push Image') {
            steps {
                withDockerRegistry([credentialsId: "dockerhub-creds", url: ""]){
                    sh 'docker tag ${IMAGE_NAME}:ci ${IMAGE_NAME}:${IMAGE_TAG}'
                    sh 'docker push ${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
