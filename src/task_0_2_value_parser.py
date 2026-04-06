"""Task 0.2: Create value parser for mixed types."""

import pandas as pd
import numpy as np
import re
from typing import Tuple, Optional

excel_file = "input/Talent Engineering Metrics.xlsx"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']


class ValueParser:
    """Parser for mixed-type metric values."""
    
    def __init__(self):
        self.parse_stats = {
            'numeric_parsed': 0,
            'x_markers': 0,
            'narrative_text': 0,
            'empty_nulls': 0,
            'other': 0,
            'parse_errors': []
        }
    
    def parse_value(self, val) -> Tuple[Optional[float], Optional[str], str]:
        """
        Parse a value and return (numeric_value, flag, original_value).
        
        Returns:
            (numeric_value, flag, original_string)
            flag can be:
                - None: Successfully parsed as numeric
                - 'X_MARKER': Single 'x' indicating data not collected/applicable
                - 'NARRATIVE': Long text with context/notes (not actual data)
                - 'NA': Null/NaN/empty
                - 'UNCERTAIN': Could not definitively parse
        """
        # Handle null/NaN
        if pd.isna(val):
            self.parse_stats['empty_nulls'] += 1
            return None, 'NA', 'NULL'
        
        val_str = str(val).strip()
        
        # Handle empty string
        if val_str == "" or val_str.lower() == "nan":
            self.parse_stats['empty_nulls'] += 1
            return None, 'NA', val_str
        
        # Handle 'x' marker (data not collected)
        if val_str.lower() == 'x':
            self.parse_stats['x_markers'] += 1
            return None, 'X_MARKER', val_str
        
        # Try to extract first numeric value
        # Match: integers, decimals, numbers with commas, negative numbers
        numeric_match = re.search(r'-?\d+\.?\d*', val_str)
        
        if numeric_match:
            try:
                numeric_val = float(numeric_match.group())
                
                # Check if this looks like a narrative (long text with numbers inside)
                if len(val_str) > 50 and numeric_match.start() > 5:
                    self.parse_stats['narrative_text'] += 1
                    return numeric_val, 'NARRATIVE', val_str[:60] + "..."
                
                # Check if it's just a number with minor formatting
                if len(val_str) < 20:
                    self.parse_stats['numeric_parsed'] += 1
                    return numeric_val, None, val_str
                
                # Long string with number - keep the number but flag it
                self.parse_stats['numeric_parsed'] += 1
                return numeric_val, 'NARRATIVE', val_str[:60] + "..."
            
            except ValueError:
                pass
        
        # If we get here, couldn't parse as numeric
        self.parse_stats['other'] += 1
        return None, 'UNCERTAIN', val_str[:60]
    
    def parse_column(self, series):
        """Parse all values in a column."""
        results = []
        for val in series:
            numeric_val, flag, original = self.parse_value(val)
            results.append({
                'numeric': numeric_val,
                'flag': flag,
                'original': original
            })
        return pd.DataFrame(results)


print("=" * 100)
print("TASK 0.2: VALUE PARSER FOR MIXED TYPES")
print("=" * 100)

parser = ValueParser()

# Parse each month and show statistics
print("\nParsing results by month:")
print("-" * 100)

all_parsed_results = {}

for month in months:
    print(f"\n{month}:")
    
    # Parse the column
    parsed = parser.parse_column(df[month])
    all_parsed_results[month] = parsed
    
    # Count by flag
    flag_counts = parsed['flag'].value_counts(dropna=False).to_dict()
    
    print(f"  Total values: {len(parsed)}")
    print(f"  Parse results:")
    for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"    - {flag}: {count}")
    
    # Show examples of narrative text that was parsed
    narrative_examples = parsed[parsed['flag'] == 'NARRATIVE']
    if len(narrative_examples) > 0:
        print(f"  Narrative examples (extracted first numeric):")
        for idx, row in narrative_examples.head(3).iterrows():
            print(f"    Value: {row['numeric']} | Original: {row['original'][:55]}")

print("\n" + "-" * 100)
print("OVERALL PARSING STATISTICS")
print("-" * 100)
print(f"Numeric successfully parsed: {parser.parse_stats['numeric_parsed']}")
print(f"X markers (data not collected): {parser.parse_stats['x_markers']}")
print(f"Narrative text flagged: {parser.parse_stats['narrative_text']}")
print(f"Empty/Null values: {parser.parse_stats['empty_nulls']}")
print(f"Other/Uncertain: {parser.parse_stats['other']}")

print("\n" + "-" * 100)
print("SAMPLE PARSING OUTPUT")
print("-" * 100)

# Show sample rows with all months parsed
sample_indices = [0, 1, 2, 10, 50, 100]
print("\nSample parsed data (Team, Metric, and all months):")

for idx in sample_indices:
    if idx < len(df):
        print(f"\nRow {idx}: {df.iloc[idx]['Team']} - {df.iloc[idx]['Metric'][:40]}")
        for month in months:
            parsed = all_parsed_results[month]
            row = parsed.iloc[idx]
            if row['flag'] is None and pd.notna(row['numeric']):
                print(f"  {month:12s}: {row['numeric']:10.2f} ✓")
            elif row['flag'] is not None:
                flag_str = str(row['flag']) if row['flag'] is not None else 'None'
                orig_str = str(row['original'])[:20] if row['original'] else ''
                print(f"  {month:12s}: {flag_str:15s} ({orig_str})")
            else:
                print(f"  {month:12s}: EMPTY")

print("\n" + "-" * 100)
print("POTENTIAL ISSUES FOUND")
print("-" * 100)

# Find metrics that have mostly narrative or NA values
issue_metrics = []
for idx in range(len(df)):
    metric_name = df.iloc[idx]['Metric']
    
    # Skip if metric name is missing
    if pd.isna(metric_name):
        continue
    
    row_flags = [all_parsed_results[month].iloc[idx]['flag'] for month in months]
    numeric_count = sum(1 for f in row_flags if f is None)
    narrative_count = sum(1 for f in row_flags if f == 'NARRATIVE')
    na_count = sum(1 for f in row_flags if f == 'NA')
    
    total_months = len(months)
    
    # Flag if mostly narrative or NA (less than 3 numeric values)
    if numeric_count < 3 and (narrative_count > 2 or na_count > 5):
        issue_metrics.append({
            'metric': str(metric_name)[:50],
            'numeric': numeric_count,
            'narrative': narrative_count,
            'na': na_count
        })

if issue_metrics:
    print("\nMetrics with data quality issues (mixed narrative/NA):")
    for issue in issue_metrics[:10]:
        print(f"  • {issue['metric']}")
        print(f"    Numeric: {issue['numeric']}, Narrative: {issue['narrative']}, NA: {issue['na']}")
else:
    print("No significant data quality issues detected.")

print("\n" + "=" * 100)
print("END OF ANALYSIS - Parser is ready for Phase 0.3")
print("=" * 100)
