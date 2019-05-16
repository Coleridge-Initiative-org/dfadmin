void setBuildStatus(String message, String state) {
	  step([
	      $class: "GitHubCommitStatusSetter",
	      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/my-org/my-repo"],
	      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
	      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
	      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
	  ]);
	}

pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = '441870321480.dkr.ecr.us-east-1.amazonaws.com/dfadmin'
        IMAGE_TAG = 'latest'
        GIT_COMMIT_HASH = sh (script: "git rev-parse --short `git log -n 1 --pretty=format:'%H'`", returnStdout: true)
        GIT_COMMITER = sh (script: "git show -s --pretty=%an", returnStdout: true)
    }

    stages {
        stage ('Start') {
              steps {
            // send build started notifications
                  slackSend (color: '#FFFF00', message: "STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' by ${env.GIT_COMMITER} #${env.GIT_COMMIT_HASH}  (${env.BUILD_URL})")
              }
        }
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
                sh 'docker build . -t ${IMAGE_NAME}:ci'
            }
        }
//        parallel {
            stage('Scan') {
                steps {
                    echo 'Scanning..'
                    sh '$(aws ecr get-login --no-include-email)'
                    sh 'docker push ${IMAGE_NAME}:ci'
                    writeFile file: "anchore_images", text: "${IMAGE_NAME}:ci"
                    anchore name: "anchore_images"
                }
            }
            stage('Test') {
                steps {
                    echo 'Testing..'
                    sh 'docker-compose up -d'
                    sh 'sleep 15s'
                    sh 'make test || true'
                    sh 'make check || true'
    //                junit '**/target/*.xml'
                }
            }
//        }
        stage('Stopping') {
            steps {
                echo 'Stopping DFAdmin..'
                sh 'docker-compose stop || true'
            }
        }
        stage('QA') {
            steps {
                echo 'Checking code..'
//                sh 'make codacy-report'
            }
        }

        stage('Push Image') {
            steps {
                sh '$(aws ecr get-login --no-include-email)'
                sh 'docker tag ${IMAGE_NAME}:ci ${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker push ${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker tag ${IMAGE_NAME}:ci ${IMAGE_NAME}:${GIT_COMMIT_HASH}'
                sh 'docker push ${IMAGE_NAME}:${GIT_COMMIT_HASH}'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
    post {
	    success {
	      slackSend (color: '#00FF00', message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})");
	      setBuildStatus("Build succeeded", "SUCCESS");
	    }
	    failure {
	      slackSend (color: '#FF0000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' by ${env.GIT_COMMITER} #${env.GIT_COMMIT_HASH} (${env.BUILD_URL})");    
	      setBuildStatus("Build failed", "FAILURE");
          sh 'docker-compose down'

	    }
    }

}