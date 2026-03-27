"""Test the membership satisfaction question"""
import pandas as pd
import sys
sys.path.insert(0, 'src')

from services.causal_inference_service import run_causal_estimation

# Load the data
df = pd.read_csv('E-commerce Customer Behavior - Sheet1.csv')

print("📊 Dataset info:")
print(f"Columns: {list(df.columns)}")
print(f"\nMembership Type values: {df['Membership Type'].unique()}")
print(f"Satisfaction Level values: {df['Satisfaction Level'].unique()}")
print(f"Discount Applied values: {df['Discount Applied'].unique()}")

# Simulate the AI plan
plan = {
    "treatment": "Membership Type",
    "outcome": "Satisfaction Level",
    "confounders": ["Age", "Total Spend", "Discount Applied"],  # AI might identify these
    "method": "backdoor"
}

schema = {}
params = {"method": "backdoor"}

print("\n🧪 Running causal estimation...")
print(f"Plan: {plan}")

try:
    results = run_causal_estimation(
        df=df,
        plan=plan,
        schema=schema,
        params=params
    )
    print("\n✅ SUCCESS!")
    print(f"Results: {results}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
