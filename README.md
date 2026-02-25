# AI Data Analyst - Auto EDA + ML Predictor

Production-focused SaaS starter that ingests CSV datasets, runs automated EDA, detects target columns, trains and evaluates ML models, explains predictions with feature importance + SHAP, supports dataset Q&A, and generates downloadable PDF reports.

## Tech Stack

- **Backend:** FastAPI, Pandas, NumPy, Scikit-learn, SHAP, Plotly, SQLAlchemy, MySQL, Joblib, XGBoost
- **Frontend:** Next.js (App Router), Tailwind CSS, Axios
- **Infra:** Docker, Docker Compose, `.env`-driven config

## Project Structure

```text
backend/
  app/
    main.py
    core/
    routes/
    services/
    models/
    schemas/
    utils/
  requirements.txt
  Dockerfile
frontend/
  app/
  components/
  lib/
  package.json
  Dockerfile
docker-compose.yml
.env.example
README.md
```

## Implemented Features

### 1) CSV Upload + Validation

- `POST /api/v1/upload`
- Accepts CSV file uploads only
- Saves file in backend storage
- Returns dataset summary:
  - rows/columns
  - column names
  - data types
  - missing values

### 2) Auto EDA

- `GET /api/v1/eda/{dataset_id}`
- Returns structured JSON for:
  - dataset overview
  - missing values
  - correlation matrix + Plotly payload
  - numerical distributions (Plotly)
  - categorical value counts (Plotly)
  - outlier counts (IQR method)
  - skewness per numeric feature

### 3) Target Detection

- `GET /api/v1/eda/detect-target/{dataset_id}`
- Heuristics:
  - excludes ID-like fields
  - binary -> classification
  - continuous numeric -> regression
  - hint-based + fallback strategy
- `POST /api/v1/ml/train` supports manual target override

### 4) ML Training Pipeline

- `POST /api/v1/ml/train`
- Auto problem type and model selection:
  - **Classification:** Logistic Regression, RandomForest, GradientBoosting
  - **Regression:** LinearRegression, RandomForestRegressor, GradientBoostingRegressor, XGBoostRegressor
- Includes:
  - train/test split
  - cross-validation
  - standard scaling for numeric features
  - one-hot encoding for categorical features
- Metrics:
  - classification: accuracy, precision, recall, f1, roc_auc
  - regression: mae, rmse, r2
- Best model persisted with Joblib

### 5) Prediction API

- `POST /api/v1/ml/predict`
- Input:
  ```json
  {
    "model_id": "model_abc123",
    "record": {"feature_1": 10, "feature_2": "A"}
  }
  ```
- Output:
  ```json
  {
    "prediction": 1,
    "probability": 0.92,
    "confidence_score": 0.84
  }
  ```

### 6) Explainability

- `GET /api/v1/ml/explain/{model_id}`
- Returns:
  - feature importance
  - SHAP summary payload (top features)

### 7) PDF Report

- `GET /api/v1/report/download-report/{model_id}`
- Includes:
  - dataset summary
  - EDA highlights
  - model comparison
  - best model metrics
  - feature importance summary
  - conclusion text

### 8) Dataset Chatbot (RAG-style analytical assistant)

- `POST /api/v1/chatbot`
- Supports safe analytical intents:
  - averages
  - totals
  - count filters (`count where age > 30`)
  - top SHAP-driven feature questions

## Frontend Pages

- `/` Home
- `/upload` Upload Dataset
- `/dashboard` Auto EDA
- `/model-results` Target detect + train + predict
- `/explainability` Explainability results
- `/chatbot` Dataset chatbot
- `/download-report` Download PDF report

## Setup Instructions

### Option A: Docker (recommended)

1. Copy environment variables:
   - `cp .env.example .env`
2. Build and start:
   - `docker compose up --build`
3. Open:
   - Frontend: `http://localhost:3000`
   - Backend docs: `http://localhost:8000/docs`

### Option B: Local Development

#### Backend

1. `cd backend`
2. `python -m venv .venv`
3. Activate virtual environment
4. `pip install -r requirements.txt`
5. Ensure MySQL is running and `.env` values are configured
6. `uvicorn app.main:app --reload`

#### Frontend

1. `cd frontend`
2. `npm install`
3. Set `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
4. `npm run dev`

## API Reference

- `POST /api/v1/upload`
- `GET /api/v1/eda/{dataset_id}`
- `GET /api/v1/eda/detect-target/{dataset_id}`
- `POST /api/v1/ml/train`
- `POST /api/v1/ml/predict`
- `GET /api/v1/ml/explain/{model_id}`
- `POST /api/v1/chatbot`
- `GET /api/v1/report/download-report/{model_id}`

## Architecture Overview

- `routes/` expose REST interfaces
- `services/` implement domain logic:
  - ingestion
  - EDA
  - target detection
  - model training
  - explainability
  - report generation
  - chatbot logic
- `models/` persist dataset/model metadata
- `storage/` stores uploaded datasets, trained models, and generated reports

## Bonus: Authentication Status

JWT auth is not yet enabled in this starter. Additions needed:

- user table + password hashing
- login/register endpoints
- JWT token issuance + middleware
- tenant-level dataset/model ownership

## Screenshot Placeholders

- Home dashboard: `docs/screenshots/home.png`
- Upload flow: `docs/screenshots/upload.png`
- EDA page: `docs/screenshots/eda.png`
- Model results: `docs/screenshots/model-results.png`
- Explainability: `docs/screenshots/explainability.png`
- Chatbot: `docs/screenshots/chatbot.png`
