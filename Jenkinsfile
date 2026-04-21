pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'ap-south-1'
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
                bat "docker build --no-cache -t churn-app ."
            }
        }

        stage('Stop Old Container') {
            steps {
                bat "docker stop churn-container || exit 0"
                bat "docker rm churn-container || exit 0"
            }
        }

        stage('Run Container') {
            steps {
                bat """
                docker run -d -p 8001:8000 --name churn-container ^
                -e AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID% ^
                -e AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY% ^
                -e AWS_DEFAULT_REGION=ap-south-1 ^
                churn-app
                """

                // ⏳ Wait for container to start
                bat "timeout /t 10"
            }
        }

        stage('Test API') {
            steps {
                bat """
                echo Testing model-status...
                curl http://localhost:8001/model-status

                echo Testing prediction...
                curl -X POST http://localhost:8001/predict ^
                -H "Content-Type: application/json" ^
                -d "{\\"gender\\":\\"Male\\",\\"SeniorCitizen\\":0,\\"Partner\\":\\"Yes\\",\\"Dependents\\":\\"No\\",\\"tenure\\":5,\\"PhoneService\\":\\"Yes\\",\\"PaperlessBilling\\":\\"Yes\\",\\"MonthlyCharges\\":70,\\"TotalCharges\\":350,\\"MultipleLines\\":\\"No\\",\\"InternetService\\":\\"DSL\\",\\"OnlineSecurity\\":\\"Yes\\",\\"OnlineBackup\\":\\"No\\",\\"DeviceProtection\\":\\"No\\",\\"TechSupport\\":\\"Yes\\",\\"StreamingTV\\":\\"No\\",\\"StreamingMovies\\":\\"No\\",\\"Contract\\":\\"Month-to-month\\",\\"PaymentMethod\\":\\"Electronic check\\"}"
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