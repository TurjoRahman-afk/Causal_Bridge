import pandas as pd

# Load the CSV
df = pd.read_csv("E-commerce Customer Behavior - Sheet1.csv")

print("=" * 80)
print("CSV COLUMNS:")
print("=" * 80)
for i, col in enumerate(df.columns):
    print(f"{i+1}. '{col}' (type: {type(col)}, length: {len(col)}, repr: {repr(col)})")

print("\n" + "=" * 80)
print("TESTING COLUMN ACCESS:")
print("=" * 80)

# Test accessing the problematic column
try:
    print(f"✅ df['Discount Applied'] works: {df['Discount Applied'].iloc[0]}")
except KeyError as e:
    print(f"❌ df['Discount Applied'] FAILED: {e}")

# Test if there are any spaces or special characters
discount_col = [c for c in df.columns if 'discount' in c.lower()]
print(f"\n🔍 Columns with 'discount': {discount_col}")

# Test normalization
def normalize(name):
    return name.replace(' ', '').replace('_', '').replace('-', '').lower()

print(f"\n🔍 Normalized 'Discount Applied': '{normalize('Discount Applied')}'")
for col in df.columns:
    if 'discount' in col.lower():
        print(f"🔍 Normalized '{col}': '{normalize(col)}'")
