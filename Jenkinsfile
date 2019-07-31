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

    environment {
        PROJECT_NAME = 'dfadmin'
        IMAGE_NAME = '441870321480.dkr.ecr.us-east-1.amazonaws.com/dfadmin'
        // IMAGE_TAG = 'latest'
        IMAGE_TAG = sh (script: "date +'secure_%Y-%m-%d_%H-%M-%S'", returnStdout: true)
        GIT_COMMIT_HASH = sh (script: "git rev-parse --short `git log -n 1 --pretty=format:'%H'`", returnStdout: true)
        GIT_COMMITER = sh (script: "git show -s --pretty=%an", returnStdout: true)
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
                sh 'docker build . -t ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH}'
                sh 'docker tag ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH} ${PROJECT_NAME}:${GIT_COMMIT_HASH}'
            }
        }
        stage('Verify') {
            parallel {
                stage('Vulnerability Scan') {
                    steps {
                        sh '$(aws ecr get-login --no-include-email)'
                        sh 'docker push ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH}'
                        writeFile file: "anchore_images", text: "${IMAGE_NAME}:ci-${GIT_COMMIT_HASH}"
                        anchore name: "anchore_images"
                    }
                }
                stage('Test') {
                    steps {
                        sh 'export GIT_COMMIT_HASH=${GIT_COMMIT_HASH}'
                        sh 'docker-compose up -d --force-recreate'
                        sh 'sleep 15s'
                        sh 'make check'
                        sh 'make jenkins'
                        junit 'reports/junit.xml'
                    }
                }

             }
        }
        stage('Sonarqube') {
                    environment {
                        scannerHome = tool 'SonarQubeScanner'
                    }
                    steps {
                        withSonarQubeEnv('ADRF Sonar') {
                            sh "${scannerHome}/bin/sonar-scanner"
                        }
                        timeout(time: 10, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: true
                        }
                    }
                }
        stage('Stop') {
            steps {
                echo 'Stopping DFAdmin..'
                sh 'docker-compose stop || true'
                sh 'docker-compose down || true'
                sh 'sudo rm -rf logs reports || true'

            }
        }
        stage('Release Image') {
            steps {
                sh '$(aws ecr get-login --no-include-email)'
                sh 'docker tag ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH} ${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker push ${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker tag ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH} ${IMAGE_NAME}:${GIT_COMMIT_HASH}'
                sh 'docker push ${IMAGE_NAME}:${GIT_COMMIT_HASH}'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
        stage('Clean Docker') {
            steps {
                sh 'docker rmi ${IMAGE_NAME}:ci-${GIT_COMMIT_HASH}'
                sh 'docker rmi ${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker rmi ${IMAGE_NAME}:${GIT_COMMIT_HASH}'
            }
        }
    }
    post {
        always {
         //   junit '**/nosetests.xml'
            cobertura coberturaReportFile: 'reports/coverage.xml'
         //   step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: '**/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
                sh 'sudo rm -rf logs reports || true'
        }
	    success {
	      slackSend (color: '#00FF00', message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' by ${env.GIT_COMMITER} (${env.BUILD_URL})");
	      setBuildStatus("Build succeeded", "SUCCESS");
	    }
	    failure {
	      slackSend (color: '#FF0000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' by ${env.GIT_COMMITER} (${env.BUILD_URL})");
	      setBuildStatus("Build failed", "FAILURE");
          sh 'docker-compose down'
          sh 'sudo rm -rf logs || true'
	    }
    }

}
