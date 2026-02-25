# AI Data Analyst - Auto EDA + ML Predictor

## 1. Introduction

**AI Data Analyst - Auto EDA + ML Predictor** is a full-stack SaaS platform that allows users to:

1. Upload CSV datasets
2. Run automatic exploratory data analysis (EDA)
3. Detect likely target columns and ML problem type
4. Train multiple ML models automatically
5. Compare metrics and select the best model
6. Get explainability outputs (feature importance + SHAP)
7. Run predictions through API
8. Download a PDF report
9. Ask analytical questions through a chatbot interface

The system is built for extensibility and production-oriented workflows.

---

## 2. Tech Stack

### Backend

- Python
- FastAPI
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP
- Plotly
- SQLAlchemy
- MySQL
- Joblib
- ReportLab

### Frontend

- Next.js (App Router)
- React
- Tailwind CSS
- Axios

### Infrastructure

- Docker
- Docker Compose
- `.env` configuration

---

## 3. High-Level Architecture

```text
User (Browser)
   |
   v
Frontend (Next.js)
   |
   v
Backend API (FastAPI)
   |                    \
   |                     \-> File Storage (CSV, Models, Reports)
   v
MySQL (metadata: datasets, model artifacts)
```

### Core Design Principles

- Service-layer backend architecture
- Separated route/schema/model/service responsibilities
- Reproducible model artifacts with Joblib
- Frontend pages aligned to product workflow
- Docker-first deployment

---

## 4. Repository Structure

```text
backend/
  app/
    core/
      config.py
      database.py
    models/
      dataset.py
      model_artifact.py
    routes/
      upload.py
      eda.py
      ml.py
      report.py
      chatbot.py
      public_api.py
    schemas/
      upload.py
      eda.py
      ml.py
    services/
      file_service.py
      eda_service.py
      target_service.py
      training_service.py
      predict_service.py
      report_service.py
      chat_service.py
    main.py
  requirements.txt
  Dockerfile
  storage/
    uploads/
    models/
    reports/

frontend/
  app/
    page.tsx
    upload/page.tsx
    dashboard/page.tsx
    model-results/page.tsx
    explainability/page.tsx
    chatbot/page.tsx
    download-report/page.tsx
    layout.tsx
    globals.css
  components/
    Sidebar.tsx
  lib/
    api.ts
    storage.ts
  package.json
  Dockerfile

docker-compose.yml
.env.example
README.md
docs/
  README.md
  PROJECT_DOCUMENTATION.md
```

---

## 5. Backend Documentation

## 5.1 Configuration and Database

### `app/core/config.py`

- Loads environment variables using `pydantic-settings`
- Exposes runtime settings:
  - app metadata
  - CORS origins
  - MySQL credentials
  - storage directories
- Builds SQLAlchemy connection URI

### `app/core/database.py`

- Initializes SQLAlchemy engine/session
- Defines `Base` model class
- Provides `get_db()` dependency for FastAPI routes

## 5.2 Data Models

### `Dataset`

Stores uploaded CSV metadata:

- `id`
- filenames/path
- row/column counts
- column names
- dtypes
- missing values
- created timestamp

### `ModelArtifact`

Stores training outputs:

- model id
- dataset reference
- target and problem type
- best model name/path
- all metrics and best metrics
- feature importance
- SHAP summary
- confidence score

## 5.3 Route Layer

### Upload Route

- `POST /api/v1/upload`
- Validates file extension (`.csv`)
- Saves CSV
- Reads DataFrame
- Persists dataset metadata
- Returns summary payload

### EDA Route

- `GET /api/v1/eda/{dataset_id}`
  - returns full EDA JSON payload for UI visualizations
- `GET /api/v1/eda/detect-target/{dataset_id}`
  - returns auto-detected target and problem type candidates

### ML Route

- `POST /api/v1/ml/train`
  - optional manual target override
  - auto-detects target if missing
  - trains model candidates
  - picks best model
  - persists artifact + model file
- `POST /api/v1/ml/predict`
  - predicts from model id and JSON record
- `GET /api/v1/ml/explain/{model_id}`
  - returns feature importance + SHAP summary

### Report Route

- `GET /api/v1/report/download-report/{model_id}`
- `GET /api/v1/report/download-report?model_id=...`
- builds and streams PDF report

### Public Alias Route

- `POST /api/v1/predict` (alias of ml predict)
- `GET /api/v1/download-report?model_id=...` (alias)

### Chatbot Route

- `POST /api/v1/chatbot`
- accepts dataset id + question
- maps safe analytical intents to DataFrame operations

## 5.4 Service Layer

### `file_service.py`

- Ensures storage folders exist
- Stores uploaded file
- Reads CSV into DataFrame

### `eda_service.py`

Generates:

- overview
- missing values
- correlation matrix + Plotly payload
- numeric distributions + Plotly payloads
- categorical frequency plots + Plotly payloads
- outlier counts via IQR
- skewness statistics

### `target_service.py`

Heuristic target detection:

- excludes ID-like columns
- binary class detection
- continuous numeric regression detection
- hint-based naming + fallback logic

### `training_service.py`

Pipeline:

- train/test split
- preprocessing with:
  - numeric: impute + scale
  - categorical: impute + one-hot encode
- candidate model training
- CV scoring and test metrics
- best model selection
- artifact persistence with Joblib
- feature importance extraction
- SHAP summary generation

### `predict_service.py`

- loads model artifact file
- runs prediction
- returns class probability (if available)
- includes confidence score

### `report_service.py`

- creates PDF with ReportLab
- sections:
  - dataset summary
  - EDA highlights
  - model comparison
  - best metrics
  - feature importance
  - conclusion

### `chat_service.py`

Supports question patterns like:

- averages
- totals
- conditional counts (`count where age > 30`)
- top impactful SHAP feature questions

---

## 6. ML Pipeline Details

## 6.1 Problem Type

- **Classification** when target appears categorical/binary
- **Regression** when target appears continuous numeric

## 6.2 Candidate Models

### Classification

- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier

### Regression

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost Regressor

## 6.3 Evaluation Metrics

### Classification

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC (binary where possible)

### Regression

- MAE
- RMSE
- R2 score

## 6.4 Best Model Selection Strategy

- classification: maximize test F1-score
- regression: maximize test R2-score
- confidence score is CV mean

---

## 7. Frontend Documentation

## 7.1 Layout and Navigation

- `app/layout.tsx`: root shell
- `components/Sidebar.tsx`: SaaS sidebar navigation
- dark mode default styling via Tailwind and `globals.css`

## 7.2 Pages

### Home (`/`)

- Product overview and capability cards

### Upload Dataset (`/upload`)

- Upload CSV
- shows dataset summary response
- stores `dataset_id` in local storage

### Dashboard (`/dashboard`)

- calls Auto EDA endpoint
- displays EDA JSON payload

### Model Results (`/model-results`)

- detect target
- train model
- show metrics
- run predictions with JSON input
- stores `model_id` in local storage

### Explainability (`/explainability`)

- fetches feature importance and SHAP summary

### Chatbot (`/chatbot`)

- submits dataset questions
- displays analytical response + mapped query

### Download Report (`/download-report`)

- generates report download link using model id

## 7.3 Frontend Utilities

### `lib/api.ts`

- shared Axios instance
- configurable backend base URL

### `lib/storage.ts`

- local storage helpers for `dataset_id` and `model_id`

---

## 8. API Documentation

## 8.1 Health

- `GET /health`

Response:

```json
{
  "status": "ok",
  "service": "AI Data Analyst API"
}
```

## 8.2 Upload

- `POST /api/v1/upload`
- `multipart/form-data` with file field: `file`

Example Response:

```json
{
  "dataset_id": "uuid",
  "rows": 1000,
  "columns": 12,
  "column_names": ["age", "salary", "churn"],
  "dtypes": {"age": "int64", "salary": "float64", "churn": "int64"},
  "missing_values": {"age": 0, "salary": 2, "churn": 0}
}
```

## 8.3 EDA

- `GET /api/v1/eda/{dataset_id}`
- returns chart-ready JSON

- `GET /api/v1/eda/detect-target/{dataset_id}`

Example Response:

```json
{
  "detected_target": "churn",
  "problem_type": "classification",
  "candidates": ["salary", "churn"],
  "reason": "Matched target hint and binary values."
}
```

## 8.4 Train

- `POST /api/v1/ml/train`

Request:

```json
{
  "dataset_id": "uuid",
  "target_column": "churn"
}
```

Response:

```json
{
  "model_id": "model_xxxxx",
  "target_column": "churn",
  "problem_type": "classification",
  "best_model": "RandomForestClassifier",
  "best_metrics": {
    "accuracy": 0.89,
    "precision": 0.88,
    "recall": 0.89,
    "f1_score": 0.88,
    "roc_auc": 0.91
  },
  "all_metrics": {},
  "feature_importance": []
}
```

## 8.5 Predict

- `POST /api/v1/ml/predict`
- `POST /api/v1/predict` (alias)

Request:

```json
{
  "model_id": "model_xxxxx",
  "record": {"age": 32, "salary": 60000, "tenure": 2}
}
```

Response:

```json
{
  "prediction": 1,
  "probability": 0.92,
  "confidence_score": 0.84
}
```

## 8.6 Explainability

- `GET /api/v1/ml/explain/{model_id}`

## 8.7 Chatbot

- `POST /api/v1/chatbot`

Request:

```json
{
  "dataset_id": "uuid",
  "question": "What is the average salary?"
}
```

Response:

```json
{
  "question": "What is the average salary?",
  "answer": "The average of salary is 52780.1290.",
  "query_used": "df['salary'].mean()"
}
```

## 8.8 Report Download

- `GET /api/v1/report/download-report/{model_id}`
- `GET /api/v1/download-report?model_id=...` (alias)

---

## 9. Environment Variables

Copy `.env.example` to `.env` and adjust values.

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | API app name | `AI Data Analyst API` |
| `APP_ENV` | environment mode | `development` |
| `API_PREFIX` | API prefix | `/api/v1` |
| `CORS_ORIGINS` | frontend origins | `http://localhost:3000` |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | `root` |
| `MYSQL_DATABASE` | DB name | `ai_data_analyst` |
| `MYSQL_USER` | DB user | `root` |
| `MYSQL_PASSWORD` | DB password | `root` |
| `MYSQL_HOST` | DB host | `db` |
| `MYSQL_PORT` | DB port | `3306` |
| `NEXT_PUBLIC_API_URL` | frontend API base URL | `http://localhost:8000/api/v1` |

---

## 10. Local Development Guide

## 10.1 Backend

```bash
cd backend
python -m venv .venv
# activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 10.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 11. Docker Deployment Guide

1. Create environment file:

```bash
cp .env.example .env
```

2. Start full stack:

```bash
docker compose up --build
```

3. Access:

- Frontend: `http://localhost:3000`
- Backend Swagger: `http://localhost:8000/docs`

---

## 12. Data and Artifact Lifecycle

1. CSV uploaded -> stored in `backend/storage/uploads`
2. Dataset metadata persisted in MySQL
3. EDA generated dynamically from CSV
4. Training saves model bundle in `backend/storage/models`
5. Model artifact metadata persisted in MySQL
6. Report generated in `backend/storage/reports`

---

## 13. Security and Production Notes

Current baseline provides functional APIs and architecture, but production hardening should include:

- JWT authentication and authorization
- role/tenant isolation
- stricter upload limits and file scanning
- async task queue for long training jobs (Celery/RQ)
- rate limiting and request throttling
- structured logging and tracing
- model and data versioning
- object storage (S3/MinIO) for large artifacts

---

## 14. Testing Strategy (Recommended)

### Backend

- Unit tests for services:
  - target detection
  - EDA payload generation
  - training selection logic
- API integration tests with test database

### Frontend

- Component tests for forms and response rendering
- E2E tests:
  - upload -> EDA -> train -> predict -> report

---

## 15. Feature Roadmap

## Completed

- Upload + summary
- Auto EDA
- Target detection
- ML training + auto-selection
- Prediction API
- Explainability outputs
- PDF report generation
- Chatbot analytical assistant
- Full-stack Docker setup

## Pending / Next Iterations

- JWT auth (register/login/protected endpoints)
- user-level dataset/model history
- asynchronous training jobs + progress tracking
- richer chart rendering (Recharts/Plotly UI components)
- stronger RAG with embeddings + vector DB
- audit logs and monitoring dashboards

---

## 16. Troubleshooting

### API cannot connect to DB

- verify MySQL container is healthy
- verify `.env` credentials
- ensure `MYSQL_HOST=db` in Docker environment

### Frontend cannot reach backend

- verify backend container is running on port `8000`
- verify `NEXT_PUBLIC_API_URL` value

### Training errors on small datasets

- some models require minimum class counts
- provide larger dataset or manually set target

### SHAP issues on unsupported model/shape

- service includes fallback note in response
- use tree-based models for most reliable SHAP support

---

## 17. Conclusion

This documentation describes the complete implementation baseline for a production-oriented **Auto EDA + ML Predictor SaaS**.  
The system is modular and ready for the next step: authentication, async job orchestration, and enterprise-grade observability.
