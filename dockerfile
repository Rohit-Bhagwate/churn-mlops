FROM python:3.12

WORKDIR /app

COPY . .

COPY mlflow.db .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn","api.app:app", "--host","0.0.0.0","--port","8000"]