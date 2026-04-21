pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'ap-south-1'
        EC2_HOST = '3.110.117.61'
        EC2_USER = 'ubuntu'
        KEY_PATH = 'C:/Users/rohit/Downloads/churn-key.pem'
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

        stage('Save Image') {
            steps {
                bat "docker save churn-app > churn-app.tar"
            }
        }

        stage('Copy to EC2') {
            steps {
                bat """
                scp -i %KEY_PATH% -o StrictHostKeyChecking=no churn-app.tar %EC2_USER%@%EC2_HOST%:/home/ubuntu/
                """
            }
        }

        stage('Deploy to EC2') {
            steps {
                bat """
                ssh -i %KEY_PATH% -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% ^
                "docker stop churn-container || true && ^
                 docker rm churn-container || true && ^
                 docker load < churn-app.tar && ^
                 docker run -d -p 8001:8000 ^
                 -e AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% ^
                 -e AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% ^
                 -e AWS_DEFAULT_REGION=ap-south-1 ^
                 --name churn-container churn-app"
                """
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