"""
Test Google Gemini Integration
Make sure to add your API key to .env first!
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("  🧠 TESTING GOOGLE GEMINI INTEGRATION")
print("=" * 80)

print("\n📝 Setup Instructions:")
print("   1. Get FREE API key: https://aistudio.google.com/app/apikey")
print("   2. Add to .env file: GEMINI_API_KEY=your_key_here")
print("   3. Start server: uvicorn src.main:app --reload")
print("   4. Run this test!")

# Check if server is running
print("\n🔍 Checking if server is running...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running!")
    else:
        print(f"⚠️  Server responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Server is not running!")
    print("\n📌 To start the server, open a NEW terminal and run:")
    print("   uvicorn src.main:app --reload")
    print("\n   Then run this test again in this terminal.")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)

input("\n⏸️  Press Enter to start tests...")

# Test 1: Natural language question (Gemini should understand)
print("\n" + "=" * 80)
print("  TEST 1: Complex Question - 'Do employees who work overtime quit more?'")
print("=" * 80)

response = requests.post(f"{BASE_URL}/api/v1/analyze", json={
    "question": "Do employees who work overtime tend to quit more often?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {
        "treatment": "OverTime",
        "outcome": "Attrition",
        "confounders": ["Age", "MonthlyIncome", "YearsAtCompany"]
    }
})

if response.status_code == 200:
    result = response.json()
    plan = result.get('plan', {})
    
    print(f"\n✅ Analysis Complete!")
    print(f"\n📊 Plan Generated:")
    print(f"   Treatment: {plan.get('treatment')}")
    print(f"   Outcome: {plan.get('outcome')}")
    print(f"   Confounders: {plan.get('confounders')}")
    print(f"   Method: {plan.get('method')}")
    
    if 'llm_used' in plan:
        print(f"\n🧠 LLM Info:")
        print(f"   Model: {plan.get('llm_used')}")
        print(f"   Reasoning: {plan.get('llm_reasoning', 'N/A')}")
        print(f"\n✅ ✅ ✅ GEMINI IS WORKING! ✅ ✅ ✅")
    else:
        print(f"\n⚠️  Simple parser used (Gemini not configured)")
        print(f"   Check: .env file has GEMINI_API_KEY")
    
    print(f"\n📈 Results:")
    print(f"   ATE: {result['results']['ate']:.4f}")
    print(f"   P-Value: {result['results']['p_value']:.6f}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: Different question format
print("\n" + "=" * 80)
print("  TEST 2: Alternative Phrasing - 'Impact of satisfaction on retention'")
print("=" * 80)

response = requests.post(f"{BASE_URL}/api/v1/analyze", json={
    "question": "How does job satisfaction impact whether employees stay?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {
        "treatment": "JobSatisfaction",
        "outcome": "Attrition",
        "confounders": ["Age", "MonthlyIncome", "WorkLifeBalance"]
    }
})

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Analysis Complete!")
    print(f"   Treatment: {result['plan']['treatment']}")
    print(f"   Outcome: {result['plan']['outcome']}")
    print(f"   ATE: {result['results']['ate']:.4f}")
    
    if 'llm_used' in result['plan']:
        print(f"   Gemini: ✅ Working")
    else:
        print(f"   Gemini: ❌ Not configured")
else:
    print(f"❌ Error: {response.text}")

# Test 3: Question with unclear variables
print("\n" + "=" * 80)
print("  TEST 3: Vague Question - 'What makes people quit?'")
print("=" * 80)
print("\n⚠️  This test requires Gemini to infer variables from the question")
print("   Without Gemini, you must specify treatment/outcome explicitly")

response = requests.post(f"{BASE_URL}/api/v1/analyze", json={
    "question": "What factors cause employees to leave the company?",
    "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    "schema": {
        # Providing explicit schema since simple parser can't infer
        "treatment": "OverTime",  # One potential factor
        "outcome": "Attrition",
        "confounders": ["Age", "JobSatisfaction", "MonthlyIncome"]
    }
})

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Analysis Complete!")
    print(f"   ATE: {result['results']['ate']:.4f}")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "=" * 80)
print("  🎉 GEMINI TESTING COMPLETE!")
print("=" * 80)

print("\n📝 Summary:")
print("   - Gemini enables natural language questions")
print("   - Falls back to simple parser if not configured")
print("   - Get FREE API key: https://aistudio.google.com/app/apikey")
print()
