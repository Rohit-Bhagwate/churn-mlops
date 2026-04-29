import pandas as pd
from fastapi import FastAPI
import joblib
from pydantic import BaseModel, Field
import logging
import os
import uuid
from utils.logger import get_logger
import boto3
from io import BytesIO

app = FastAPI()

logger = get_logger()

#Logging setup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


S3_BUCKET = 'churn-mlops-bucket-12345'
MODEL_KEY = os.getenv("MODEL_KEY",'churn_pipeline.pkl')
#Load Trained Pipeline
try:
    logger.info("Loading model from s3...")
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket = S3_BUCKET,Key= MODEL_KEY)
    model = joblib.load(BytesIO(obj['Body'].read()))
    logger.info("Model loaded successfully from s3")
except Exception as e:
    logger.error(f"Model loading failed:{str(e)}")
    model = None

class ChurnInput(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents:str
    tenure: int = Field(gt=0)
    PhoneService: str
    PaperlessBilling: str
    MonthlyCharges: float = Field(gt=0)
    TotalCharges: float = Field(gt=0)
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaymentMethod: str

@app.get("/")
def home():
    return{"message": "Churn Prediction API is running"}

@app.get("/model-status")
def model_status():
    return{"model_loaded":model is not None,
           "model_source":"s3",
           "model_key":MODEL_KEY}

@app.on_event("startup")
def startup_event():
    logger.info("Application started successfully")

@app.get("/health")
def health():
    return {"status": "health",
            "model_loaded": model is not None}

@app.post("/predict")
def predict(data: ChurnInput):
    request_id = str(uuid.uuid4())
    try:
        if model is None:
            return{"status": "error",
                   "message": "Model not available",
                   "request_id": request_id}
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Incoming request: {data.dict()}")
        df = pd.DataFrame([data.dict()])
        prediction = model.predict(df)
        #Log out
        label = "Churn" if int(prediction[0]) == 1 else "No Churn"
        logger.info(f"[{request_id}] prediction result: {prediction.tolist()}")
        return {"status":"success",
                "request_id": request_id,
                "prediction": int(prediction[0]),
                "label":label}
    except Exception as e:
        logger.error((f"Error occured: {str(e)}"))
        return{"status":"error",
               "message": "Predicton failed",
               "request_id":request_id}

@app.get("/version")
def version():
    return {"status":"success",
            "version":"1.0"}
