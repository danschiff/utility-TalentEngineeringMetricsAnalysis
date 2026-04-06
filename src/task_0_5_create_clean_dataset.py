"""Task 0.5: Create clean dataset output - Final Phase 0 deliverable."""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
from datetime import datetime

excel_file = "input/Talent Engineering Metrics.xlsx"
output_file = "output/team_metrics_cleaned.csv"
metadata_file = "output/data_dictionary.csv"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']


class ValueParser:
    """Parser for mixed-type metric values."""
    
    def parse_value(self, val):
        if pd.isna(val):
            return None, 'NA'
        
        val_str = str(val).strip()
        if val_str == "" or val_str.lower() == "nan":
            return None, 'NA'
        
        if val_str.lower() == 'x':
            return None, 'X_MARKER'
        
        numeric_match = re.search(r'-?\d+\.?\d*', val_str)
        if numeric_match:
            try:
                numeric_val = float(numeric_match.group())
                if len(val_str) > 50:
                    return numeric_val, 'NARRATIVE'
                return numeric_val, 'VALID'
            except ValueError:
                pass
        
        return None, 'UNCERTAIN'


class BenchmarkParser:
    """Parser for benchmark ranges and percentages."""
    
    def parse_benchmark(self, val):
        result = {
            'benchmark_raw': str(val) if not pd.isna(val) else None,
            'benchmark_min': None,
            'benchmark_max': None,
            'benchmark_mid': None,
            'benchmark_unit': None,
        }
        
        if pd.isna(val):
            return result
        
        val_str = str(val).strip()
        if val_str == "" or val_str.upper() in ['TBD', 'N/A', 'NA']:
            return result
        
        # Extract unit
        unit_match = re.search(r'(days?|hours?|weeks?|month|/|%)', val_str, re.IGNORECASE)
        if unit_match:
            result['benchmark_unit'] = unit_match.group().lower()
        
        # Try to extract range
        range_patterns = [
            r'(\d+\.?\d*)\s*–\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',
            r'(\d+)\s*to\s*(\d+)',
        ]
        
        for pattern in range_patterns:
            range_match = re.search(pattern, val_str, re.IGNORECASE)
            if range_match:
                try:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    result['benchmark_min'] = min_val
                    result['benchmark_max'] = max_val
                    result['benchmark_mid'] = (min_val + max_val) / 2
                    return result
                except ValueError:
                    pass
        
        # Try single number
        single_match = re.search(r'(\d+\.?\d*)', val_str)
        if single_match:
            try:
                result['benchmark_min'] = float(single_match.group(1))
                return result
            except ValueError:
                pass
        
        return result


class MetricStandardizer:
    """Standardize metrics to consistent units and directions."""
    
    metric_standards = {
        r'(?i)(predictability|commitment|coverage|success|resolved|investment)': {'unit': '%', 'direction': 'higher_better'},
        r'(?i)(unplanned|wasted|failure|defect|attrition|regrettable)': {'unit': '%', 'direction': 'lower_better'},
        r'(?i)(cycle|time|mttr|latency|lead)': {'unit': 'time', 'direction': 'lower_better'},
        r'(?i)(incident|severity|defect|bug)': {'unit': 'count', 'direction': 'lower_better'},
        r'(?i)(resolved|created|completed|merged)': {'unit': 'count', 'direction': 'higher_better'},
    }
    
    def get_standard(self, metric_name: str) -> Dict:
        if pd.isna(metric_name):
            return {'unit': 'unknown', 'direction': 'unknown'}
        
        metric_str = str(metric_name)
        for pattern, standard in self.metric_standards.items():
            if re.search(pattern, metric_str):
                return standard
        
        return {'unit': 'count', 'direction': 'context_dependent'}


print("=" * 100)
print("TASK 0.5: CREATE CLEAN DATASET OUTPUT")
print("=" * 100)

value_parser = ValueParser()
benchmark_parser = BenchmarkParser()
standardizer = MetricStandardizer()

print("\nCompiling cleaned dataset...")
print("-" * 100)

# Process all rows
cleaned_rows = []
data_quality_stats = {'total': 0, 'with_data': 0, 'valid_parsed': 0, 'narratives': 0}

for idx, row in df.iterrows():
    # Skip rows with missing critical metadata
    team = row['Team']
    metric = row['Metric']
    metric_group = row['Metric Group']
    
    if pd.isna(metric) or str(metric).strip() == '':
        continue
    
    # Get standardization info
    standard = standardizer.get_standard(metric)
    
    # Parse benchmark
    benchmark_info = benchmark_parser.parse_benchmark(row['Industry Benchmarks'])
    
    # Create base row
    clean_row = {
        'team': team,
        'metric_group': metric_group,
        'metric': metric,
        'source': row['Source'],
        'metric_unit': standard['unit'],
        'metric_direction': standard['direction'],
        'benchmark_min': benchmark_info['benchmark_min'],
        'benchmark_max': benchmark_info['benchmark_max'],
        'benchmark_mid': benchmark_info['benchmark_mid'],
        'benchmark_unit': benchmark_info['benchmark_unit'],
    }
    
    # Parse each month
    month_data_count = 0
    for month in months:
        val = row[month]
        numeric_val, flag = value_parser.parse_value(val)
        
        clean_row[f'{month}_value'] = numeric_val
        clean_row[f'{month}_flag'] = flag
        
        if numeric_val is not None:
            month_data_count += 1
            data_quality_stats['valid_parsed'] += 1
            if flag == 'NARRATIVE':
                data_quality_stats['narratives'] += 1
    
    if month_data_count > 0:
        data_quality_stats['with_data'] += 1
    
    data_quality_stats['total'] += 1
    cleaned_rows.append(clean_row)

# Create cleaned dataframe
cleaned_df = pd.DataFrame(cleaned_rows)

print(f"\nDataset compilation complete:")
print(f"  Total metrics processed: {data_quality_stats['total']}")
print(f"  Metrics with at least one value: {data_quality_stats['with_data']} ({data_quality_stats['with_data']/data_quality_stats['total']*100:.1f}%)")
print(f"  Valid numeric values parsed: {data_quality_stats['valid_parsed']}")
print(f"  Narrative entries (with extracted numeric): {data_quality_stats['narratives']}")

print("\n" + "-" * 100)
print("CLEANED DATASET STRUCTURE")
print("-" * 100)

print(f"\nShape: {cleaned_df.shape[0]} metrics × {cleaned_df.shape[1]} columns")
print(f"\nColumn breakdown:")
print(f"  Metadata columns: 10 (team, metric_group, metric, source, etc.)")
print(f"  Benchmark columns: 4 (min, max, mid, unit)")
print(f"  Month data columns: {len([c for c in cleaned_df.columns if '_value' in c])} (9 months × 2 columns)")

print(f"\nColumn list:")
for col in cleaned_df.columns:
    print(f"  • {col}")

print("\n" + "-" * 100)
print("DATA QUALITY METRICS")
print("-" * 100)

# Calculate data completeness by team
print("\nData completeness by team:")
for team in cleaned_df['team'].unique():
    if pd.notna(team):
        team_data = cleaned_df[cleaned_df['team'] == team]
        valid_values = sum([sum(1 for v in team_data[f'{m}_value'] if pd.notna(v)) for m in months])
        total_slots = len(team_data) * len(months)
        completeness = valid_values / total_slots * 100 if total_slots > 0 else 0
        print(f"  {team:35s}: {completeness:5.1f}% ({valid_values}/{total_slots})")

# Calculate data completeness by month
print("\nData completeness by month:")
for month in months:
    non_null = sum(1 for v in cleaned_df[f'{month}_value'] if pd.notna(v))
    print(f"  {month:12s}: {non_null:3d} values ({non_null/len(cleaned_df)*100:5.1f}%)")

print("\n" + "-" * 100)
print("DATA DIRECTION DISTRIBUTION")
print("-" * 100)

direction_counts = cleaned_df['metric_direction'].value_counts()
print("\nMetrics by direction:")
for direction, count in direction_counts.items():
    print(f"  {direction:20s}: {count:3d} ({count/len(cleaned_df)*100:5.1f}%)")

print("\nMetrics by unit:")
unit_counts = cleaned_df['metric_unit'].value_counts()
for unit, count in unit_counts.items():
    print(f"  {unit:20s}: {count:3d} ({count/len(cleaned_df)*100:5.1f}%)")

print("\n" + "-" * 100)
print("BENCHMARK COVERAGE")
print("-" * 100)

benchmarked = sum(1 for v in cleaned_df['benchmark_mid'] if pd.notna(v))
print(f"Metrics with benchmarks: {benchmarked} ({benchmarked/len(cleaned_df)*100:.1f}%)")
print(f"Metrics without benchmarks: {len(cleaned_df) - benchmarked}")

print("\n" + "-" * 100)
print("SAMPLE CLEANED DATA")
print("-" * 100)

# Show 5 sample rows with key columns
sample_cols = ['team', 'metric', 'metric_direction', 'benchmark_mid', 
               'July_value', 'August_value', 'September_value', 'March_value']
available_cols = [c for c in sample_cols if c in cleaned_df.columns]

print("\nSample cleaned rows:")
print(cleaned_df[available_cols].head(5).to_string())

# Create data dictionary
print("\n" + "-" * 100)
print("CREATING DATA DICTIONARY")
print("-" * 100)

data_dict_rows = []

# Metadata columns
for col in ['team', 'metric_group', 'metric', 'source']:
    data_dict_rows.append({
        'Column Name': col,
        'Type': 'Metadata',
        'Data Type': 'string',
        'Description': f'Original {col} from source file'
    })

# Standard columns
data_dict_rows.extend([
    {
        'Column Name': 'metric_unit',
        'Type': 'Standard',
        'Data Type': 'string',
        'Description': 'Standardized metric unit: %, time, count'
    },
    {
        'Column Name': 'metric_direction',
        'Type': 'Standard',
        'Data Type': 'string',
        'Description': 'Direction of improvement: higher_better, lower_better, context_dependent'
    }
])

# Benchmark columns
for col in ['benchmark_min', 'benchmark_max', 'benchmark_mid', 'benchmark_unit']:
    data_dict_rows.append({
        'Column Name': col,
        'Type': 'Benchmark',
        'Data Type': 'float/string',
        'Description': f'Parsed benchmark {col.replace("benchmark_", "")} from industry standards'
    })

# Month value columns
for month in months:
    data_dict_rows.append({
        'Column Name': f'{month}_value',
        'Type': 'Data',
        'Data Type': 'float',
        'Description': f'Parsed numeric value for {month}'
    })
    data_dict_rows.append({
        'Column Name': f'{month}_flag',
        'Type': 'Quality Flag',
        'Data Type': 'string',
        'Description': f'Data quality flag: VALID, NA, X_MARKER, NARRATIVE, UNCERTAIN'
    })

data_dict_df = pd.DataFrame(data_dict_rows)

print(f"Data dictionary created with {len(data_dict_df)} column descriptions")

# Save outputs
print("\n" + "-" * 100)
print("SAVING OUTPUT FILES")
print("-" * 100)

try:
    cleaned_df.to_csv(output_file, index=False)
    print(f"✓ Cleaned dataset saved to: {output_file}")
    print(f"  Rows: {len(cleaned_df)}, Columns: {len(cleaned_df.columns)}")
except Exception as e:
    print(f"✗ Error saving cleaned dataset: {e}")

try:
    data_dict_df.to_csv(metadata_file, index=False)
    print(f"✓ Data dictionary saved to: {metadata_file}")
except Exception as e:
    print(f"✗ Error saving data dictionary: {e}")

print("\n" + "=" * 100)
print("TASK 0.5 COMPLETE - Phase 0 Data Cleaning Finished")
print("=" * 100)
print("\nDeliverables:")
print(f"  1. Cleaned dataset: {output_file}")
print(f"  2. Data dictionary: {metadata_file}")
print(f"\nNext Steps:")
print("  • Phase 1: Data Loading & Exploration")
print("  • Phase 2: Benchmark Comparison Analysis")
print("  • Phase 3: Trend Visualization")
print("  • Phase 4: Anomaly Detection")
