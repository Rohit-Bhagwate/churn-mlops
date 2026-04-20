import pandas as pd
from fastapi import FastAPI
import joblib
from pydantic import BaseModel, Field
import logging
import mlflow
import mlflow.pyfunc
import os
import uuid

app = FastAPI()
#Logging setup
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#Load Trained Pipeline
try:
    mlflow.set_tracking_uri("sqlite://mlflow.db")
    model = mlflow.pyfunc.load_model("models:/churn_model1/Production")
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
    logging.info("Application started successfully")

@app.get("/health")
def health():
    return {"status": "health"}

@app.post("/predict")
def predict(data: ChurnInput):
    request_id = str(uuid.uuid4())
    try:
        if model is None:
            return{"stats": "error",
                   "message": "Model not available",
                   "request_id": request_id}
        logging.info(f"Request ID: {request_id}")
        logging.info(f"Incoming request: {data.dict()}")
        df = pd.DataFrame([data.dict()])
        prediction = model.predict(df)
        #Log out
        label = "Churn" if int(prediction[0]) == 1 else "No Churn"
        logging.info(f"prediction result:{prediction.tolist()}")
        return {"status":"success",
                "request_id": request_id,
                "prediction": int(prediction[0]),
                "label":label}
    except Exception as e:
        logging.error((f"Error occured: {str(e)}"))
        return{"status":"error",
               "message": "Predicton failed",
               "request_id":request_id}

@app.get("/version")
def version():
    return {"status":"error",
            "version":"1.0"}
