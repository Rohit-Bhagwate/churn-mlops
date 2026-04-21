pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'ap-south-1'
        EC2_HOST = 'YOUR_EC2_PUBLIC_IP'
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

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-key']) {
                    bat """
                    ssh -o StrictHostKeyChecking=no ubuntu@%EC2_HOST% ^
                    "docker stop churn-container || true && ^
                     docker rm churn-container || true && ^
                     docker pull churn-app || true && ^
                     docker run -d -p 8001:8000 ^
                     -e AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% ^
                     -e AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% ^
                     -e AWS_DEFAULT_REGION=ap-south-1 ^
                     --name churn-container churn-app"
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