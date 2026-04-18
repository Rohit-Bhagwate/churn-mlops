import mlflow.pyfunc
import mlflow
import pandas as pd
mlflow.set_tracking_uri("file:./mlruns")
#Lodad model from mlflow

model = mlflow.pyfunc.load_model("models:/churn_model1/Production")

#Example input
input_data = [{"gender":"Male",
               "SeniorCitizen":0,
               "Partner":"Yes",
               "Dependents":"No",
               "tenure":12,
               "PhoneService":"Yes",
               "PaperlessBilling":"Yes",
               "MonthlyCharges":70.5,
               "TotalCharges":850.5,
               "MultipleLines":"No",
               "InternetService":"Fiber optic",
               "OnlineSecurity":"No",
               "OnlineBackup":"Yes",
               "DeviceProtection":"No",
               "TechSupport":"No",
               "StreamingTV":"Yes",
               "StreamingMovies":"Yes",
               "Contract":"Month-to-month",
               "PaymentMethod":"Credit card (automatic)"}]

#Predict
df = pd.DataFrame(input_data)
prediction = model.predict(df)
print("Prediction:",prediction)