import pandas as pd
from fastapi import FastAPI
import joblib
from pydantic import BaseModel, Field
import logging
import mlflow
import mlflow.pyfunc
import os
import uuid
from utils.logger import get_logger

app = FastAPI()

logger = get_logger()

#Logging setup
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mlflow.set_tracking_uri(f"sqlite:///{os.path.join(BASE_DIR,'mlflow.db')}")

#Load Trained Pipeline
try:
    print("Loading model from MLflow...")
    MODEL_PATH = os.path.join(BASE_DIR, "model", "churn_pipeline.pkl")
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Model loading failes:{str(e)}")
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

@app.on_event("startup")
def startup_event():
    logger.info("Application started successfully")

@app.get("/health")
def health():
    return {"status": "health"}

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
        logger.info(f"prediction result:{prediction.tolist()}")
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
    return {"status":"error",
            "version":"1.0"}
