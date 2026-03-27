"""
Test script for HR Employee Attrition dataset
Dataset: WA_Fn-UseC_-HR-Employee-Attrition.csv

This script tests various causal questions on the HR dataset:
- Effect of overtime on attrition
- Effect of job satisfaction on attrition
- Effect of monthly income on attrition
- Effect of years at company on attrition
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_overtime_effect():
    """Test: Does working overtime increase employee attrition?"""
    print_section("TEST 1: Effect of Overtime on Attrition")
    
    payload = {
        "question": "What is the effect of overtime on attrition?",
        "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "schema": {
            "treatment": "OverTime",
            "outcome": "Attrition",
            "confounders": ["Age", "MonthlyIncome", "YearsAtCompany", "JobSatisfaction"]
        },
        "params": {
            "method": "backdoor",
            "confidence_level": 0.95
        }
    }
    
    print("\n📊 Analyzing: Does overtime cause attrition?")
    print(f"Treatment: OverTime (Yes/No)")
    print(f"Outcome: Attrition (Yes/No)")
    print(f"Confounders: Age, MonthlyIncome, YearsAtCompany, JobSatisfaction\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", {})
                print("✅ Analysis Complete!")
                print(f"\n📈 Results:")
                print(f"   Average Treatment Effect: {results.get('ate', 'N/A'):.4f}")
                print(f"   95% Confidence Interval: [{results.get('confidence_interval', ['N/A', 'N/A'])[0]:.4f}, {results.get('confidence_interval', ['N/A', 'N/A'])[1]:.4f}]")
                print(f"   P-Value: {results.get('p_value', 'N/A'):.6f}")
                print(f"   Statistical Significance: {'Yes (p < 0.05)' if results.get('p_value', 1) < 0.05 else 'No (p >= 0.05)'}")
                print(f"\n   Sample Size (Treated): {results.get('n_treated', 'N/A')}")
                print(f"   Sample Size (Control): {results.get('n_control', 'N/A')}")
                
                # Interpretation
                ate = results.get('ate', 0)
                if results.get('p_value', 1) < 0.05:
                    if ate > 0:
                        print(f"\n💡 Interpretation: Overtime INCREASES attrition risk by {ate:.4f} units")
                    else:
                        print(f"\n💡 Interpretation: Overtime DECREASES attrition risk by {abs(ate):.4f} units")
                else:
                    print(f"\n💡 Interpretation: No statistically significant effect detected")
            else:
                print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running with: uvicorn src.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_job_satisfaction_effect():
    """Test: Does job satisfaction affect attrition?"""
    print_section("TEST 2: Effect of Job Satisfaction on Attrition")
    
    payload = {
        "question": "What is the impact of job satisfaction on attrition?",
        "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "schema": {
            "treatment": "JobSatisfaction",
            "outcome": "Attrition",
            "confounders": ["Age", "MonthlyIncome", "WorkLifeBalance", "YearsAtCompany"]
        },
        "params": {
            "method": "backdoor"
        }
    }
    
    print("\n📊 Analyzing: Does job satisfaction reduce attrition?")
    print(f"Treatment: JobSatisfaction (1-4 scale)")
    print(f"Outcome: Attrition (Yes/No)")
    print(f"Confounders: Age, MonthlyIncome, WorkLifeBalance, YearsAtCompany\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", {})
                print("✅ Analysis Complete!")
                print(f"\n📈 Results:")
                print(f"   Average Treatment Effect: {results.get('ate', 'N/A'):.4f}")
                print(f"   95% Confidence Interval: [{results.get('confidence_interval', ['N/A', 'N/A'])[0]:.4f}, {results.get('confidence_interval', ['N/A', 'N/A'])[1]:.4f}]")
                print(f"   P-Value: {results.get('p_value', 'N/A'):.6f}")
                
                # Interpretation
                ate = results.get('ate', 0)
                if results.get('p_value', 1) < 0.05:
                    if ate < 0:
                        print(f"\n💡 Interpretation: Higher job satisfaction REDUCES attrition by {abs(ate):.4f} units per satisfaction level")
                    else:
                        print(f"\n💡 Interpretation: Higher job satisfaction INCREASES attrition by {ate:.4f} units (unexpected!)")
                else:
                    print(f"\n💡 Interpretation: No statistically significant effect detected")
        else:
            print(f"❌ Request failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_income_effect():
    """Test: Does monthly income affect attrition?"""
    print_section("TEST 3: Effect of Monthly Income on Attrition")
    
    payload = {
        "question": "What is the effect of monthly income on attrition?",
        "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "schema": {
            "treatment": "MonthlyIncome",
            "outcome": "Attrition",
            "confounders": ["Age", "Education", "JobLevel", "YearsAtCompany"]
        },
        "params": {
            "method": "backdoor"
        }
    }
    
    print("\n📊 Analyzing: Does higher income reduce attrition?")
    print(f"Treatment: MonthlyIncome (continuous)")
    print(f"Outcome: Attrition (Yes/No)")
    print(f"Confounders: Age, Education, JobLevel, YearsAtCompany\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", {})
                print("✅ Analysis Complete!")
                print(f"\n📈 Results:")
                print(f"   Average Treatment Effect: {results.get('ate', 'N/A'):.6f}")
                print(f"   95% Confidence Interval: [{results.get('confidence_interval', ['N/A', 'N/A'])[0]:.6f}, {results.get('confidence_interval', ['N/A', 'N/A'])[1]:.6f}]")
                print(f"   P-Value: {results.get('p_value', 'N/A'):.6f}")
                
                # Interpretation
                ate = results.get('ate', 0)
                if results.get('p_value', 1) < 0.05:
                    if ate < 0:
                        print(f"\n💡 Interpretation: Each $1000 increase in income REDUCES attrition by {abs(ate*1000):.4f} units")
                    else:
                        print(f"\n💡 Interpretation: Each $1000 increase in income INCREASES attrition by {ate*1000:.4f} units")
                else:
                    print(f"\n💡 Interpretation: No statistically significant effect detected")
        else:
            print(f"❌ Request failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_years_at_company_effect():
    """Test: Does tenure affect attrition?"""
    print_section("TEST 4: Effect of Years at Company on Attrition")
    
    payload = {
        "question": "What is the impact of years at company on attrition?",
        "dataset_uri": "WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "schema": {
            "treatment": "YearsAtCompany",
            "outcome": "Attrition",
            "confounders": ["Age", "MonthlyIncome", "JobSatisfaction", "WorkLifeBalance"]
        },
        "params": {
            "method": "backdoor"
        }
    }
    
    print("\n📊 Analyzing: Does tenure reduce attrition?")
    print(f"Treatment: YearsAtCompany (continuous)")
    print(f"Outcome: Attrition (Yes/No)")
    print(f"Confounders: Age, MonthlyIncome, JobSatisfaction, WorkLifeBalance\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results = result.get("results", {})
                print("✅ Analysis Complete!")
                print(f"\n📈 Results:")
                print(f"   Average Treatment Effect: {results.get('ate', 'N/A'):.4f}")
                print(f"   95% Confidence Interval: [{results.get('confidence_interval', ['N/A', 'N/A'])[0]:.4f}, {results.get('confidence_interval', ['N/A', 'N/A'])[1]:.4f}]")
                print(f"   P-Value: {results.get('p_value', 'N/A'):.6f}")
                
                # Interpretation
                ate = results.get('ate', 0)
                if results.get('p_value', 1) < 0.05:
                    if ate < 0:
                        print(f"\n💡 Interpretation: Each additional year at company REDUCES attrition by {abs(ate):.4f} units")
                    else:
                        print(f"\n💡 Interpretation: Each additional year at company INCREASES attrition by {ate:.4f} units")
                else:
                    print(f"\n💡 Interpretation: No statistically significant effect detected")
        else:
            print(f"❌ Request failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  🔬 HR EMPLOYEE ATTRITION - CAUSAL ANALYSIS TEST SUITE")
    print("=" * 80)
    print("\nDataset: WA_Fn-UseC_-HR-Employee-Attrition.csv")
    print("Testing various causal questions about employee attrition\n")
    
    # Run all tests
    test_overtime_effect()
    test_job_satisfaction_effect()
    test_income_effect()
    test_years_at_company_effect()
    
    print("\n" + "=" * 80)
    print("  ✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\n💡 Summary: These analyses help HR understand what factors")
    print("   causally influence employee attrition, enabling data-driven")
    print("   retention strategies.\n")

if __name__ == "__main__":
    main()
