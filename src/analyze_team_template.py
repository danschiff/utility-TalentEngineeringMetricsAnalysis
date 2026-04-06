"""Analyze the Team-Level Template worksheet."""

import pandas as pd
import numpy as np

excel_file = "input/Talent Engineering Metrics.xlsx"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")

print("=" * 100)
print("TEAM-LEVEL TEMPLATE ANALYSIS")
print("=" * 100)

# Basic info
print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns")

# Column names and data types
print(f"\nColumn Names and Data Types:")
print("-" * 100)
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col:40s} → {str(df[col].dtype):15s}")

# First 15 rows
print(f"\nFirst 15 rows of data:")
print("-" * 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
print(df.head(15).to_string())

# Summary statistics for numeric columns
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    print(f"\n\nSummary Statistics (Numeric Columns):")
    print("-" * 100)
    print(df[numeric_cols].describe().to_string())

# Missing values
print(f"\n\nMissing Values:")
print("-" * 100)
missing = df.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0].to_string())
else:
    print("No missing values found")

# Info about non-numeric columns
print(f"\n\nNon-Numeric Column Analysis:")
print("-" * 100)
non_numeric_cols = df.select_dtypes(exclude=['number']).columns
for col in non_numeric_cols:
    unique_count = df[col].nunique()
    print(f"\n{col}:")
    print(f"  Unique values: {unique_count}")
    if unique_count <= 20:
        print("  Value counts:")
        print(df[col].value_counts().to_string())

print("\n" + "=" * 100)
print("END OF ANALYSIS")
print("=" * 100)
