"""
Quick test for column matching functionality
"""

def normalize_column_name(name: str) -> str:
    """Normalize column name by removing spaces, underscores, and converting to lowercase."""
    return name.replace(' ', '').replace('_', '').replace('-', '').lower()

def find_matching_column(target: str, available_columns: list) -> str:
    """
    Find a matching column name with fuzzy matching.
    """
    # First try exact match
    if target in available_columns:
        return target
    
    # Try normalized matching
    target_normalized = normalize_column_name(target)
    for col in available_columns:
        if normalize_column_name(col) == target_normalized:
            return col
    
    # No match found
    return None

# Test cases
test_cases = [
    ("Discount Applied", ["Date", "Sales", "Discount_Applied", "Revenue"]),
    ("discount applied", ["Date", "Sales", "DiscountApplied", "Revenue"]),
    ("Sales Revenue", ["Date", "SalesRevenue", "Cost", "Profit"]),
    ("customer_id", ["CustomerID", "Name", "Age"]),
]

print("🧪 Testing Column Matching:")
print("=" * 60)

for target, available in test_cases:
    result = find_matching_column(target, available)
    status = "✅" if result else "❌"
    print(f"{status} Looking for: '{target}'")
    print(f"   Available: {available}")
    print(f"   Found: '{result}'" if result else "   NOT FOUND")
    print()
