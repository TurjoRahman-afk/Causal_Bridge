# 🚀 CausalBridge v2.0 - NEW FEATURES!

> **For developers & technical documentation:** See [README.md](README.md) for API reference, installation details, and architecture.

## 🎉 What's New

### 1. **Advanced Causal Methods**
Now fully integrated and ready to use:

- **Propensity Score Matching (PSM)** - Perfect for binary treatments (Yes/No)
- **Difference-in-Differences (DiD)** - For before/after comparisons  
- **Instrumental Variables (IV)** - When you have hidden confounding

### 2. **Web Dashboard** 
Beautiful, easy-to-use interface:
- Drag & drop file upload
- Ask questions in plain English
- Real-time results with AI explanations
- Professional visualizations

### 3. **Multi-Format Support**
Now accepts:
- ✅ CSV files (.csv)
- ✅ Excel files (.xlsx, .xls)
- ✅ JSON files (.json)
- ✅ Parquet files (.parquet)

## 🚀 Quick Start

### Option 1: Web Dashboard (Easiest!)
```powershell
# Start the server
.\start_server.ps1

# Open your browser to:
# http://localhost:8000
```

Then:
1. Upload your dataset (drag & drop)
2. Ask your question in plain English
3. Get AI-powered insights!

### Option 2: Python API
```python
import requests

response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "question": "Does overtime affect employee attrition?",
    "dataset_uri": "uploads/your_data.csv",
    "schema": {},  # Let Gemini figure it out!
    "params": {"method": "propensity_score_matching"}
})

print(response.json())
```

### Option 3: Command Line
```powershell
python test_real_questions.py
```

## 🎯 Advanced Method Examples

### Propensity Score Matching (PSM)
**Best for:** Binary treatments like Yes/No, On/Off

```python
{
    "question": "Do employees who work overtime quit more?",
    "dataset_uri": "employee_data.xlsx",
    "params": {"method": "propensity_score_matching"}
}
```

**When to use:** 
- Treatment is binary (OverTime: Yes/No)
- Want to match similar treated/control units
- More robust than simple regression

### Difference-in-Differences (DiD)
**Best for:** Before/after policy changes

```python
{
    "question": "Did the new policy reduce turnover?",
    "dataset_uri": "policy_data.csv",
    "schema": {
        "time_variable": "after_policy",  # 0=before, 1=after
        "group_variable": "treatment_group"  # 0=control, 1=treated
    },
    "params": {"method": "difference_in_differences"}
}
```

**When to use:**
- Have data from before AND after an intervention
- Have both treatment and control groups
- Want to control for time trends

### Instrumental Variables (IV)
**Best for:** When you suspect hidden confounding

```python
{
    "question": "Does education cause higher wages?",
    "dataset_uri": "wages.json",
    "schema": {
        "instrument": "distance_to_college"  # Affects education but not wages directly
    },
    "params": {"method": "instrumental_variable"}
}
```

**When to use:**
- Worried about unmeasured confounders
- Have a valid instrument (affects treatment, not outcome)
- Need stronger causal claims

## 📊 File Format Examples

### CSV
```csv
EmployeeID,OverTime,Attrition,Age,Salary
1,Yes,Yes,32,50000
2,No,No,45,75000
```

### Excel (.xlsx)
Same structure as CSV, but with Excel formatting

### JSON
```json
[
    {"EmployeeID": 1, "OverTime": "Yes", "Attrition": "Yes"},
    {"EmployeeID": 2, "OverTime": "No", "Attrition": "No"}
]
```

## 🧠 Gemini AI Tips

The smarter your question, the better Gemini understands:

**Good questions:**
- ✅ "Do employees who work overtime quit more often?"
- ✅ "What's the impact of job satisfaction on retention?"
- ✅ "Does monthly income affect whether people stay?"

**Less helpful:**
- ❌ "correlation between X and Y" (not causal)
- ❌ "analyze data" (too vague)

## 🎨 Dashboard Features

1. **Drag & Drop Upload** - No coding needed
2. **Smart Method Selection** - Gemini recommends the best method
3. **Real-time Results** - See effects instantly
4. **Data Quality Warnings** - Get alerted to potential issues
5. **Beautiful Visualizations** - Professional charts and graphs

## 🔧 API Endpoints

- `GET /` - Web Dashboard
- `GET /docs` - API Documentation (Swagger UI)
- `POST /api/v1/upload` - Upload dataset
- `POST /api/v1/analyze` - Run causal analysis
- `GET /api/v1/datasets` - List uploaded files
- `GET /api/v1/visualize` - Generate charts

## 📈 Performance

- **Speed:** <5 seconds for most analyses
- **Capacity:** Up to 100MB datasets
- **Accuracy:** Bootstrap confidence intervals
- **AI:** Google Gemini 2.5 Flash (FREE!)

## ⚡ Pro Tips

1. **Always check data quality warnings** - they tell you about potential issues
2. **Use PSM for binary treatments** - more robust than regression
3. **Let Gemini suggest confounders** - it's smart about finding them!
4. **Upload Excel files** - no need to convert to CSV
5. **Ask multiple questions** - each analysis takes ~3 seconds

## 🐛 Troubleshooting

**Dashboard not loading?**
```powershell
# Make sure server is running:
.\start_server.ps1

# Check: http://localhost:8000
```

**File upload fails?**
- Check file format (CSV, Excel, JSON, Parquet)
- Make sure file is < 100MB
- Check file has proper column names

**Gemini not working?**
```powershell
# Verify API key:
python -c "from src.core.config import settings; print('Key loaded:', bool(settings.gemini_api_key))"
```

## 🎓 Learn More

- [README.md](README.md) - Full documentation
- [GEMINI_SETUP.md](GEMINI_SETUP.md) - AI configuration
- [test_real_questions.py](test_real_questions.py) - Example usage

## 🚀 What's Next?

Coming soon:
- PDF report generation
- Batch analysis (multiple questions at once)
- Database connections (PostgreSQL, MySQL)
- Plotly interactive charts
- Sensitivity analysis

---

**Version:** 2.0.0  
**Updated:** January 25, 2026  
**AI Powered by:** Google Gemini 2.5 Flash 🧠
