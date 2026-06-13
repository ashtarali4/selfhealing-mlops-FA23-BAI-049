pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "ashtar049"
        IMAGE_UNSTABLE = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE   = "${DOCKERHUB_USER}/sentiment-api:stable"
        EC2_IP         = "98.82.242.170"
        APP_PORT       = "5000"
        CONTAINER_NAME = "sentiment-test"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh """
                    docker build -t ${IMAGE_UNSTABLE} .
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        -v /app/logs:/app/logs \
                        ${IMAGE_UNSTABLE}
                    sleep 20
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        ${IMAGE_UNSTABLE} \
                        pytest tests/test_api.py -v
                """
            }
        }

        stage('UI Test') {
            steps {
                sh """
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        ${IMAGE_UNSTABLE} \
                        pytest tests/test_ui.py -v
                """
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                        # Push unstable image
                        docker push ${IMAGE_UNSTABLE}

                        # Build and push stable image from stable-fallback branch
                        git fetch origin stable-fallback
                        git stash
                        git checkout stable-fallback
                        docker build -t ${IMAGE_STABLE} .
                        docker push ${IMAGE_STABLE}

                        # Return to main
                        git checkout main
                        git stash pop || true

                        docker logout
                    """
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh """
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=120s
                """
            }
        }

    }

    post {
        always {
            sh "docker rm -f ${CONTAINER_NAME} || true"
        }
        success {
            echo 'CI Pipeline completed successfully!'
        }
        failure {
            echo 'CI Pipeline failed.'
        }
    }
}
