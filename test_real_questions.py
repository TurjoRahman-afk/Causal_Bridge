"""
Test CausalBridge with Real-Life Questions
This demonstrates Gemini's ability to understand natural language
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("  🧠 TESTING REAL-LIFE CAUSAL QUESTIONS WITH GEMINI")
print("=" * 80)

# Check server
try:
    requests.get(f"{BASE_URL}/health", timeout=2)
    print("\n✅ Server is running!\n")
except:
    print("\n❌ Server not running! Start with: uvicorn src.main:app --reload\n")
    exit(1)

# Real-life questions to test
questions = [
    {
        "question": "Does working overtime increase the chance of employees quitting?",
        "context": "HR wants to understand if overtime is causing attrition"
    },
    {
        "question": "Are employees with higher job satisfaction less likely to leave?",
        "context": "Testing if satisfaction programs reduce turnover"
    },
    {
        "question": "Does monthly income affect whether people stay at the company?",
        "context": "Checking if salary increases would reduce attrition"
    },
    {
        "question": "Do younger employees quit more than older ones?",
        "context": "Understanding age-related retention patterns"
    },
    {
        "question": "Does the number of years at the company reduce attrition risk?",
        "context": "Testing if tenure creates loyalty"
    }
]

for i, test in enumerate(questions, 1):
    print("=" * 80)
    print(f"  QUESTION {i}: {test['question']}")
    print("=" * 80)
    print(f"💡 Context: {test['context']}")
    print()
    
    # Call API - provide minimal schema, let Gemini enhance it
    response = requests.post(f"{BASE_URL}/api/v1/analyze", json={
        "question": test['question'],
        "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "schema": {
            # Providing empty confounders - let Gemini suggest them
            "confounders": []
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        plan = result.get('plan', {})
        results = result.get('results', {})
        
        print("🎯 What Gemini Understood:")
        print(f"   • Treatment (cause): {plan.get('treatment')}")
        print(f"   • Outcome (effect): {plan.get('outcome')}")
        print(f"   • Method chosen: {plan.get('method')}")
        print(f"   • Confounders suggested: {', '.join(plan.get('confounders', []))}")
        
        if 'llm_used' in plan:
            print(f"\n🧠 Gemini's Reasoning:")
            reasoning = plan.get('llm_reasoning', '')
            # Wrap long text
            words = reasoning.split()
            line = "   "
            for word in words:
                if len(line + word) > 77:
                    print(line)
                    line = "   " + word + " "
                else:
                    line += word + " "
            if line.strip():
                print(line)
        
        print(f"\n📊 Results:")
        ate = results.get('ate', 0)
        p_value = results.get('p_value', 1)
        ci = results.get('confidence_interval', [])
        
        print(f"   • Effect size (ATE): {ate:.4f}")
        print(f"   • Statistical significance: {'✅ Significant' if p_value < 0.05 else '❌ Not significant'} (p={p_value:.4f})")
        if ci:
            print(f"   • 95% Confidence Interval: [{ci[0]:.4f}, {ci[1]:.4f}]")
        
        # Interpretation
        print(f"\n💬 Plain English:")
        if 'OverTime' in plan.get('treatment', ''):
            if ate > 0:
                print(f"   Working overtime increases attrition by {abs(ate)*100:.1f} percentage points")
            else:
                print(f"   Working overtime decreases attrition by {abs(ate)*100:.1f} percentage points")
        elif 'Satisfaction' in plan.get('treatment', ''):
            if ate < 0:
                print(f"   Each 1-point increase in satisfaction reduces attrition by {abs(ate)*100:.1f}%")
            else:
                print(f"   Higher satisfaction increases attrition by {ate*100:.1f}%")
        elif 'Income' in plan.get('treatment', ''):
            if ate < 0:
                print(f"   Higher income reduces attrition")
            else:
                print(f"   Higher income increases attrition")
        elif 'Age' in plan.get('treatment', ''):
            if ate < 0:
                print(f"   Older employees are less likely to quit")
            else:
                print(f"   Older employees are more likely to quit")
        elif 'Years' in plan.get('treatment', ''):
            if ate < 0:
                print(f"   Longer tenure reduces attrition risk")
            else:
                print(f"   Longer tenure increases attrition risk")
        
        # Data quality warnings
        quality = results.get('data_quality', {})
        warnings = quality.get('warnings', [])
        if warnings:
            print(f"\n⚠️  Data Quality Warnings:")
            for warning in warnings[:3]:  # Show top 3
                print(f"   • {warning}")
        
    else:
        print(f"❌ Error: {response.text}")
    
    print()

print("=" * 80)
print("  🎉 TESTING COMPLETE!")
print("=" * 80)
print("\n💡 Tips:")
print("   • Gemini automatically identifies treatment and outcome from your question")
print("   • It suggests relevant confounders based on the dataset")
print("   • It chooses appropriate causal methods")
print("   • Just ask questions naturally - Gemini handles the rest!")
print()
