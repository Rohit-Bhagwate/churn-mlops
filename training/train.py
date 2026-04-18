import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
import joblib
import mlflow
import mlflow.sklearn
import os


mlflow.set_tracking_uri("file:./mlruns")

#Load data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR,"data","WA_Fn-UseC_-Telco-Customer-Churn.csv")
df = pd.read_csv(data_path)

#Cleaning Data
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors='coerce')
df = df.drop("customerID",axis=1)
df['Churn'] = df["Churn"].map({"Yes":1,"No":0})
df = df.dropna()
#Split features and target
X = df.drop("Churn", axis=1)
y = df["Churn"]

#Train Test Split
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2,random_state=42)

categorical_cols = X.select_dtypes(include=['object']).columns
numerical_cols = X.select_dtypes(exclude=['object']).columns

#Processor
preprocessor = ColumnTransformer(transformers=[("num",StandardScaler(),numerical_cols),
                                 ("cat",OneHotEncoder(drop='first',handle_unknown='ignore')
                                  ,categorical_cols)])

#pipeline
pipeline = Pipeline(steps=[("preprocessor",preprocessor),
                           ("model",LogisticRegression())])

mlflow.set_experiment("churn_prediction")


with mlflow.start_run() as run:

    pipeline.fit(X_train,y_train)

    y_pred = pipeline.predict(X_test)

    #Evaluation
    acc = accuracy_score(y_test,y_pred)
    print("Accuracy:",acc)
    mlflow.log_metric("accuracy",acc)

    #Model Saving
    model_dir = os.path.join(BASE_DIR, "model")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "churn_pipeline.pkl")
    joblib.dump(pipeline, model_path)
    mlflow.sklearn.log_model(pipeline,"model")

    print("RUN ID:",run.info.run_id)