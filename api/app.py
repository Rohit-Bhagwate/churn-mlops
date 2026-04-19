import pandas as pd
from fastapi import FastAPI
import joblib
from pydantic import BaseModel, Field
import logging
import mlflow
import mlflow.pyfunc
import os

app = FastAPI()
#Logging setup
logging.basicConfig(level=logging.INFO,filename="app.log",filemode="a",format="%(asctime)s - (levelname)s - %(message)")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#Load Trained Pipeline
mlflow.set_tracking_uri("sqlite:///mlflow.db")
model = joblib.load("model/churn_pipeline.pkl")

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

@app.post("/predict")
def predict(data: ChurnInput):
    try:
        logging.info(f"Input Data: {data.dict()}")
        df = pd.DataFrame([data.dict()])
        prediction = model.predict(df)
        #Log out
        logging.info(f"prediction:{prediction}")
        label = "Churn" if int(prediction[0]) == 1 else "No Churn"
        return {"prediction": int(prediction[0]),
                "label":label}
    except Exception as e:
        logging.error((f"Error occured: {e}"))
        return{"error": str(e)}
