# CausalBridge

An AI-powered causal inference platform that transforms natural-language business questions into statistically valid causal estimates — no statistics PhD required.

> **🚀 New to CausalBridge?** Check out [VERSION_2.0.md](VERSION_2.0.md) for a quick start guide, new features, and user-friendly examples!

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [API Key Setup](#api-key-setup)
6. [Running the Project](#running-the-project)
7. [Using the Dashboard](#using-the-dashboard)
8. [API Endpoints](#api-endpoints)
9. [Supported Causal Methods](#supported-causal-methods)
10. [Configuration Reference](#configuration-reference)
11. [Roadmap](#roadmap)

---

## Overview

CausalBridge allows anyone to perform causal inference analysis by asking questions in plain English:

1. Upload your dataset (CSV, Excel, JSON, or Parquet)
2. Ask a question like *"Does a discount cause higher customer satisfaction?"*
3. The AI (Groq/Gemini) identifies what to test and what to control for
4. The statistical engine runs a peer-reviewed causal method
5. You get a clear result: effect size, confidence interval, p-value, and plain-English interpretation

---

## Features

- **Natural Language Questions** — Ask in English, get scientific answers
- **AI-Powered Parsing** — Groq (LLaMA 3.3 70B) or Google Gemini understands your question
- **4 Causal Methods** — Backdoor Adjustment, Propensity Score Matching, Difference-in-Differences, Instrumental Variables
- **Interactive Dashboard** — Upload data, run analysis, view charts — all in the browser
- **RESTful API** — Integrate CausalBridge into any existing system
- **Data Quality Checks** — Automatic validation before analysis runs
- **Multi-format Support** — CSV, Excel (.xlsx), JSON, Parquet

---

## Project Structure

```
CausalBridge/
├── src/
│   ├── main.py                          # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py                    # Core API endpoints (/analyze, /health)
│   │   ├── upload_routes.py             # File upload endpoints
│   │   ├── visualization_routes.py      # Chart/visualization endpoints
│   │   └── dependencies.py             # Dependency injection
│   ├── services/
│   │   ├── nlp_service_gemini.py        # AI question parsing (Groq + Gemini)
│   │   ├── nlp_service.py              # Fallback rule-based parser
│   │   ├── causal_inference_service.py  # Statistical estimation engine
│   │   ├── advanced_causal_methods.py   # DiD, IV, PSM implementations
│   │   ├── data_quality.py             # Pre-analysis data validation
│   │   └── validation_service.py       # Request validation
│   ├── models/
│   │   ├── request_models.py           # Pydantic request schemas
│   │   └── response_models.py          # Pydantic response schemas
│   ├── core/
│   │   ├── config.py                   # App settings (reads from .env)
│   │   └── exceptions.py              # Custom exceptions
│   └── utils/
│       └── __init__.py
├── static/
│   └── dashboard.html                  # Web dashboard (single-page app)
├── uploads/                            # Uploaded dataset files (auto-created)
├── tests/                              # Test suite
├── .env                                # Environment variables (API keys, settings)
├── requirements.txt                    # Python dependencies
├── start_server.ps1                    # One-click server start (PowerShell)
└── README.md                           # This file
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- PowerShell (Windows) or Bash (Mac/Linux)

### Steps

**1. Navigate to the project folder:**
```powershell
cd "d:\DESKTOP\Projects\CausalBridge\CausalBridge\CausalBridge"
```

**2. Create a virtual environment:**
```powershell
python -m venv .venv
```

**3. Activate the virtual environment:**
```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Mac / Linux
source .venv/bin/activate
```

**4. Install all dependencies:**
```powershell
pip install -r requirements.txt
```

---

## API Key Setup

CausalBridge uses a free AI service to understand your natural language questions.  
You need **one** of the following free API keys:

---

### Option A — Groq (Recommended ✅)
> **Free. No credit card. 14,400 requests/day.**

1. Go to **https://console.groq.com**
2. Sign up with Google or GitHub (no credit card needed)
3. Click **API Keys** in the left sidebar → **Create API Key**
4. Copy the key (starts with `gsk_...`)
5. Open the `.env` file and paste it:
```env
GROQ_API_KEY=gsk_your_key_here
```

---

### Option B — Google Gemini
> **Free. Requires Google account. 1,500 requests/day.**

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key (starts with `AIzaSy...`)
5. Open the `.env` file and paste it:
```env
GEMINI_API_KEY=AIzaSy_your_key_here
```

---

### How the AI fallback chain works
```
You ask a question
        ↓
Gemini key set? → Uses Gemini
        ↓ (if not set or fails)
Groq key set?   → Uses Groq
        ↓ (if not set or fails)
Manual mode     → You specify Treatment & Outcome manually in the dashboard
```

> **Note:** If neither key is set, the app still works — you just manually select the Treatment and Outcome columns in the dashboard instead of typing a plain-English question.

---

## Running the Project

### Option A — One-click script (Easiest)

Make sure your virtual environment is activated, then run:

```powershell
.\start_server.ps1
```

### Option B — Manual command

```powershell
uvicorn src.main:app --reload
```

### Option C — With custom host/port

```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Once started, you will see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## Using the Dashboard

Open your browser and go to:

| Page | URL |
|---|---|
| 🖥️ **Main Dashboard** | http://127.0.0.1:8000/dashboard |
| 📖 **API Docs (Swagger)** | http://127.0.0.1:8000/docs |
| 📄 **API Docs (ReDoc)** | http://127.0.0.1:8000/redoc |

### Dashboard Workflow

1. **Upload** your CSV/Excel file using the Upload section
2. **Type your question** in plain English, e.g.:
   - *"Does having a gold membership cause higher satisfaction?"*
   - *"Does overtime work lead to employee attrition?"*
   - *"Does applying a discount increase the number of items purchased?"*
3. *(Optional)* Manually select **Treatment**, **Outcome**, and **Method** if you prefer
4. Click **Analyze** and wait a few seconds
5. View the results: effect size, confidence interval, p-value, and interpretation

---

## API Endpoints

### `POST /api/v1/analyze`
Run a causal analysis.

**Request:**
```json
{
  "question": "Does overtime cause attrition?",
  "dataset_uri": "uploads/your_file.csv",
  "schema": {
    "treatment": "OverTime",
    "outcome": "Attrition",
    "confounders": ["Age", "MonthlyIncome", "JobSatisfaction"]
  },
  "params": {
    "method": "backdoor",
    "confidence_level": 0.95
  }
}
```

**Response:**
```json
{
  "success": true,
  "plan": {
    "treatment": "OverTime",
    "outcome": "Attrition",
    "method": "backdoor",
    "llm_used": "Groq (LLaMA 3.3 70B)"
  },
  "results": {
    "ate": 0.18,
    "confidence_interval": [0.12, 0.24],
    "p_value": 0.001,
    "n_treated": 416,
    "n_control": 1054
  },
  "message": "Analysis completed successfully"
}
```

### `POST /api/v1/upload`
Upload a dataset file (CSV, Excel, JSON, Parquet).

### `GET /api/v1/columns/{filename}`
Get the list of column names from an uploaded file.

### `GET /health`
Basic health check.

### `GET /api/v1/health`
API health check with version info.

---

## Supported Causal Methods

| Method | Flag | Best For |
|---|---|---|
| **Backdoor Adjustment** | `backdoor` | Continuous treatments, regression-based control |
| **Propensity Score Matching** | `propensity_score_matching` | Binary treatments (Yes/No, 0/1) |
| **Difference-in-Differences** | `difference_in_differences` | Before/after policy comparisons |
| **Instrumental Variables** | `instrumental_variable` | When hidden confounders are suspected |

The AI automatically recommends the best method based on your data. You can also override it manually.

---

## Configuration Reference

All settings live in the `.env` file at the project root:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `CausalBridge` | Application name |
| `DEBUG` | `True` | Enable debug logging |
| `LLM_PROVIDER` | `Groq` | Active AI provider (`Groq` or `Gemini`) |
| `GROQ_API_KEY` | *(empty)* | Your Groq API key — get free at https://console.groq.com |
| `GEMINI_API_KEY` | *(empty)* | Your Gemini API key — get free at https://aistudio.google.com/app/apikey |
| `DEFAULT_METHOD` | `backdoor` | Default causal inference method |
| `SEED` | `42` | Random seed for reproducibility |
| `CONFIDENCE_LEVEL` | `0.95` | Statistical confidence level (95%) |
| `MAX_DATASET_SIZE_MB` | `100` | Maximum allowed file upload size |

---

## Roadmap

- [x] AI question parsing — Gemini ✅ and Groq ✅
- [x] Backdoor Adjustment ✅
- [x] Propensity Score Matching ✅
- [x] Difference-in-Differences ✅
- [x] Instrumental Variables ✅
- [x] Interactive web dashboard ✅
- [x] Multi-format file support (CSV, Excel, JSON, Parquet) ✅
- [x] Data quality validation ✅
- [ ] PDF report generation
- [ ] Authentication and rate limiting
- [ ] Batch analysis (multiple questions at once)
- [ ] Database integration for result history
- [ ] Async processing for very large datasets

---

## License

This project is licensed under the MIT License.

## Overview

CausalBridge allows users to perform causal inference analysis by asking questions in natural language. The system:
1. Accepts a natural language question about causal relationships
2. Translates it into a causal analysis plan
3. Executes the plan on provided datasets
4. Returns statistical results with confidence intervals

## Features

- **Natural Language Processing**: Convert business questions into structured plans for causal analysis
- **Multiple Causal Methods**: Support for backdoor adjustment, propensity score matching, and more
- **Statistical Validation**: Confidence intervals, p-values, and bootstrap estimates
- **RESTful API**: Easy integration with existing systems
- **Comprehensive Validation**: Input validation and error handling

## Project Structure

```
CausalBridge/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # API endpoints
│   │   └── dependencies.py    # Dependency injection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py            # Question parsing & plan generation
│   │   ├── causal_inference_service.py # Statistical estimation
│   │   └── validation_service.py      # Request validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py   # Pydantic request models
│   │   └── response_models.py  # Pydantic response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Application settings
│   │   └── exceptions.py      # Custom exceptions
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py         # Helper functions
│   └── main.py                # FastAPI application
├── tests/                     # Test suite
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project metadata
└── README.md               # This file
```

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd CausalBridge
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
DEBUG=True
```

## Usage

### Starting the Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the effect of education on income?",
    "dataset_uri": "data/income_data.csv",
    "schema": {
      "treatment": "education_years",
      "outcome": "annual_income",
      "confounders": ["age", "gender", "experience"]
    },
    "params": {
      "method": "backdoor",
      "confidence_level": 0.95
    }
  }'
```

### Example Response

```json
{
  "success": true,
  "plan": {
    "treatment": "education_years",
    "outcome": "annual_income",
    "confounders": ["age", "gender", "experience"],
    "method": "backdoor",
    "effect_type": "ATE"
  },
  "results": {
    "ate": 5000.0,
    "confidence_interval": [4500.0, 5500.0],
    "p_value": 0.001,
    "n_treated": 500,
    "n_control": 500,
    "standard_error": 250.0
  },
  "message": "Analysis completed successfully"
}
```

## API Endpoints

### POST /api/v1/analyze
Perform causal analysis on a dataset based on a natural language question.

**Request Body**:
- `question` (string): Natural language causal question
- `dataset_uri` (string): Path to dataset (CSV, JSON, or Parquet)
- `schema` (object): Dataset schema with treatment, outcome, and confounders
- `params` (object, optional): Additional parameters like method and confidence level

**Response**:
- `success` (boolean): Whether the analysis succeeded
- `plan` (object): Generated analysis plan
- `results` (object): Statistical results including ATE, CI, p-value
- `message` (string): Status message

### GET /health
Health check endpoint

### GET /api/v1/health
API health check endpoint

## Supported Causal Methods

- **Backdoor Adjustment**: Default method using regression with confounders
- **Propensity Score Matching**: Match treated and control units
- **Instrumental Variables**: (Placeholder for future implementation)
- **Regression Discontinuity**: (Placeholder for future implementation)

## Configuration

Configuration is managed through the `src/core/config.py` file and can be overridden with environment variables:

- `APP_NAME`: Application name (default: "CausalBridge")
- `DEBUG`: Debug mode (default: True)
- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `DEFAULT_METHOD`: Default causal inference method (default: "backdoor")
- `SEED`: Random seed for reproducibility (default: 42)
- `CONFIDENCE_LEVEL`: Default confidence level (default: 0.95)
- `MAX_DATASET_SIZE_MB`: Maximum dataset size in MB (default: 100)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [x] LLM integration for advanced question parsing (Gemini AI ✅)
- [x] Support for more causal inference methods (PSM, DiD, IV ✅)
- [x] Data visualization endpoints (✅)
- [x] Multi-format file support (CSV, Excel, JSON, Parquet ✅)
- [ ] PDF report generation
- [ ] Authentication and rate limiting
- [ ] Database integration for result storage
- [ ] Async processing for large datasets
- [ ] Batch analysis (multiple questions at once)

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.