# 🎉 Google Gemini Integration - Setup Guide

## ✅ What's Installed

Google Gemini is now integrated into your CausalBridge! It's **100% FREE** and gives you:
- 🧠 Smart question understanding (any format)
- 💡 Automatic confounder suggestions
- 🎯 Method recommendations
- 📝 Reasoning explanations

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get Your FREE API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key (looks like: `AIzaSy...`)

### Step 2: Add to Your Project

Create or edit `.env` file in your project root:

```env
# Application Settings
APP_NAME=CausalBridge
DEBUG=True

# LLM Settings
LLM_PROVIDER=Gemini

# Google Gemini API Key (FREE!)
GEMINI_API_KEY=AIzaSy_your_actual_key_here

# Leave these empty (not needed)
OPENAI_API_KEY=
```

### Step 3: Restart Your Server

```powershell
# Kill the current server (Ctrl+C)
# Then restart:
uvicorn src.main:app --reload
```

### Step 4: Test It!

```powershell
python test_new_features.py
```

---

## 🎯 What Gemini Enables

### Before (Without Gemini):
```python
{
  "question": "What is the effect of X on Y?",  # Only these 2 patterns work
  "schema": {
    "treatment": "X",        # You MUST specify
    "outcome": "Y",          # You MUST specify
    "confounders": ["A", "B"]  # You MUST provide
  }
}
```

### After (With Gemini):
```python
{
  "question": "Does working overtime make employees quit?",  # ANY format!
  "schema": {},  # Gemini figures it out!
  # Or just provide dataset columns, Gemini suggests everything
}
```

**Gemini understands:**
- "Does X cause Y?"
- "How does X affect Y?"
- "What's the relationship between X and Y?"
- "If I increase X, what happens to Y?"
- ANY natural language question!

---

## 📊 Example: Advanced Usage

```python
import requests

# Complex question - Gemini figures it out!
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "question": "If employees work overtime, are they more likely to quit?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {}  # Empty! Gemini will extract treatment, outcome, and suggest confounders
})

result = response.json()

# Gemini's analysis:
print(result['plan']['treatment'])    # "OverTime"
print(result['plan']['outcome'])      # "Attrition"
print(result['plan']['confounders'])  # ["Age", "MonthlyIncome", "JobSatisfaction", ...]
print(result['plan']['llm_reasoning'])  # "OverTime is binary and directly affects..."
```

---

## 🆓 Gemini Free Tier Limits

- ✅ **60 requests per minute** (very generous!)
- ✅ **1,500 requests per day**
- ✅ **1 million tokens per month**
- ✅ **No credit card required**
- ✅ **Never expires**

For your use case (analyzing HR data a few times per day), this is more than enough!

---

## 🔧 Troubleshooting

### Error: "API key not found"
- Make sure `.env` file is in the project root
- Check the key starts with `AIzaSy`
- Restart the server

### Gemini not being used:
- Check `LLM_PROVIDER=Gemini` in `.env`
- Verify `GEMINI_API_KEY` is set
- Server must be restarted after changing `.env`

### Fallback to simple parser:
- If Gemini fails, system automatically falls back to simple parser
- No errors - it just works!
- Check server logs for "Warning: Gemini API error"

---

## 🎯 Testing Gemini

Create `test_gemini.py`:

```python
import requests

# Test 1: Complex question
print("Test 1: Natural language question")
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "question": "Do employees who work overtime tend to leave the company?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {}
})

result = response.json()
if 'llm_used' in result['plan']:
    print(f"✅ Gemini was used!")
    print(f"   Treatment: {result['plan']['treatment']}")
    print(f"   Outcome: {result['plan']['outcome']}")
    print(f"   Reasoning: {result['plan']['llm_reasoning']}")
else:
    print(f"⚠️  Fell back to simple parser (check API key)")

# Test 2: Different question format
print("\nTest 2: Another question format")
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "question": "How does job satisfaction impact employee retention?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {}
})

result = response.json()
print(f"   Treatment: {result['plan']['treatment']}")
print(f"   Outcome: {result['plan']['outcome']}")
```

Run it:
```powershell
python test_gemini.py
```

---

## 🎉 You're All Set!

Your CausalBridge now has FREE AI-powered question understanding! 

**Next steps:**
1. Get your API key: https://aistudio.google.com/app/apikey
2. Add to `.env` file
3. Restart server
4. Try complex questions!

Questions? Check the logs or test without Gemini - everything still works! 🚀
