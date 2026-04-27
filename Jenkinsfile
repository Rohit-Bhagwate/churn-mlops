pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'ap-south-1'
        EC2_HOST = '13.232.154.54'
        ECR_REPO = '232932848445.dkr.ecr.ap-south-1.amazonaws.com/churn-app'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/Rohit-Bhagwate/churn-mlops.git'
            }
        }

        stage('Build Image') {
            steps {
                bat "docker build -t churn-app ."
            }
        }

        stage('Login to ECR') {
            steps {
                bat """
                aws ecr get-login-password --region %AWS_DEFAULT_REGION% | docker login --username AWS --password-stdin %ECR_REPO%
                """
            }
        }

        stage('Tag Image') {
            steps {
                bat "docker tag churn-app %ECR_REPO%:latest"
            }
        }

        stage('Push to ECR') {
            steps {
                bat "docker push %ECR_REPO%:latest"
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'ec2-key', keyFileVariable: 'KEY')]) {
                    bat """
                    icacls "%KEY%" /inheritance:r
                    icacls "%KEY%" /grant:r SYSTEM:R
                    ssh -i "%KEY%" -o StrictHostKeyChecking=no ubuntu@%EC2_HOST% "docker stop churn-container || true && docker rm churn-container || true && docker pull %ECR_REPO%:latest && docker run -d -p 8001:8000 -e AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% -e AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% -e AWS_DEFAULT_REGION=ap-south-1 --name churn-container %ECR_REPO%:latest"
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful"
        }
        failure {
            echo "Deployment failed"
        }
    }
}