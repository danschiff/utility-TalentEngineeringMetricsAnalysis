"""Task 0.1: Analyze month column patterns to understand data formats."""

import pandas as pd
import numpy as np
from collections import Counter
import re

excel_file = "input/Talent Engineering Metrics.xlsx"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")

# Focus on month columns
months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']

print("=" * 100)
print("TASK 0.1: MONTH COLUMN PATTERN ANALYSIS")
print("=" * 100)

# Function to categorize value types
def categorize_value(val):
    """Categorize a value by its type/format."""
    if pd.isna(val):
        return "NULL"
    
    val_str = str(val).strip()
    
    if val_str == "" or val_str.lower() == "nan":
        return "EMPTY_STRING"
    
    # Check for percentage
    if "%" in val_str:
        return "PERCENTAGE"
    
    # Check for range (e.g., "80 – 85", "5 - 8")
    if "–" in val_str or " - " in val_str:
        return "RANGE"
    
    # Check for pure number
    try:
        float(val_str)
        return "NUMERIC"
    except ValueError:
        pass
    
    # Check for text that might have units
    if any(unit in val_str for unit in ['days', 'hours', 'month', 'weeks', 'per', 'PDR']):
        return "TEXT_WITH_UNITS"
    
    # Generic text
    return "TEXT"

print("\n" + "-" * 100)
print("PATTERN ANALYSIS BY MONTH")
print("-" * 100)

# Analyze each month column
for month in months:
    print(f"\n{month}:")
    print("-" * 50)
    
    col_data = df[month].dropna()  # Remove NaN
    
    if len(col_data) == 0:
        print("  No non-null values")
        continue
    
    # Categorize all values
    categories = [categorize_value(val) for val in col_data]
    category_counts = Counter(categories)
    
    print(f"  Total values: {len(col_data)}")
    print(f"  Categories found:")
    for category, count in category_counts.most_common():
        print(f"    - {category}: {count}")
    
    # Show sample values for each category
    print(f"  Sample values by category:")
    for category in sorted(set(categories)):
        samples = [str(col_data.iloc[i]) for i, c in enumerate(categories) if c == category][:3]
        print(f"    {category}: {samples}")

print("\n" + "-" * 100)
print("DETAILED SAMPLE VALUES")
print("-" * 100)

# Show 20 random rows with values across all months
sample_indices = np.random.choice(df.index, size=min(20, len(df)), replace=False)
sample_df = df.loc[sample_indices, ['Team', 'Metric'] + months]

print("\nSample data (20 random rows):")
print(sample_df.to_string())

print("\n" + "-" * 100)
print("VALUE FORMAT EXAMPLES")
print("-" * 100)

# Collect unique format examples
all_values = []
for month in months:
    all_values.extend(df[month].dropna().unique())

print(f"\nTotal unique values across all months: {len(set(all_values))}")
print("\nExamples of different formats found:")

format_examples = {
    'PERCENTAGE': [],
    'RANGE': [],
    'NUMERIC': [],
    'TEXT_WITH_UNITS': [],
    'TEXT': []
}

for val in all_values:
    category = categorize_value(val)
    if len(format_examples[category]) < 3:
        format_examples[category].append(str(val))

for category, examples in format_examples.items():
    if examples:
        print(f"\n  {category}:")
        for ex in examples:
            print(f"    → '{ex}'")

print("\n" + "=" * 100)
print("END OF ANALYSIS")
print("=" * 100)
