"""Task 0.4: Standardize units and metric values."""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
from collections import defaultdict

excel_file = "input/Talent Engineering Metrics.xlsx"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']


class MetricStandardizer:
    """Standardize metrics to consistent units and directions."""
    
    def __init__(self):
        # Mapping of metric names/patterns to their properties
        self.metric_standards = {
            # Percentages (higher is better)
            r'(?i)(predictability|commitment|coverage|success|resolved|investment)': {
                'unit': '%',
                'direction': 'higher_better',
                'scale': (0, 100)
            },
            # Percentages (lower is better)
            r'(?i)(unplanned|wasted|failure|defect|attrition|regrettable)': {
                'unit': '%',
                'direction': 'lower_better',
                'scale': (0, 100)
            },
            # Time metrics (lower is better)
            r'(?i)(cycle|time|mttr|latency|lead)': {
                'unit': 'time',
                'direction': 'lower_better',
                'scale': None  # Depends on unit
            },
            # Incidents (lower is better)
            r'(?i)(incident|severity|defect|bug)': {
                'unit': 'count',
                'direction': 'lower_better',
                'scale': (0, None)
            },
            # Positive counts (higher is better)
            r'(?i)(resolved|created|completed|merged)': {
                'unit': 'count',
                'direction': 'higher_better',
                'scale': (0, None)
            },
            # Load/allocation (context dependent, default lower for utilization)
            r'(?i)(load|allocation|utilization|capacity)': {
                'unit': 'count',
                'direction': 'context_dependent',
                'scale': (0, None)
            }
        }
        
        self.stats = defaultdict(int)
    
    def identify_metric_standard(self, metric_name: str) -> Dict:
        """Identify the standard for a metric based on its name."""
        
        if pd.isna(metric_name):
            return {'unit': 'unknown', 'direction': 'unknown', 'scale': None}
        
        metric_str = str(metric_name)
        
        # Check each pattern
        for pattern, standard in self.metric_standards.items():
            if re.search(pattern, metric_str):
                return standard
        
        # Default: treat as generic count
        return {
            'unit': 'count',
            'direction': 'context_dependent',
            'scale': (0, None)
        }
    
    def normalize_value(self, value, standard: Dict) -> Tuple[float, str]:
        """
        Normalize a value based on its standard.
        
        Returns: (normalized_value, status_flag)
        """
        if pd.isna(value):
            return None, 'NULL'
        
        try:
            val = float(value)
        except (ValueError, TypeError):
            return None, 'NON_NUMERIC'
        
        # For percentage scales, ensure 0-100 range
        if standard['unit'] == '%':
            if val < 0 or val > 100:
                # Might be in decimal form (0-1), check if likely
                if 0 <= val <= 1:
                    val = val * 100
                    return val, 'SCALED_0_TO_1'
                else:
                    return None, 'OUT_OF_RANGE'
        
        return val, 'VALID'


print("=" * 100)
print("TASK 0.4: STANDARDIZE UNITS AND METRIC VALUES")
print("=" * 100)

standardizer = MetricStandardizer()

# Analyze all metrics and their standards
print("\nAnalyzing metric standards:")
print("-" * 100)

metric_standards_map = {}
for i, row in df.iterrows():
    metric_name = row['Metric']
    metric_group = row['Metric Group']
    
    if pd.isna(metric_name):
        continue
    
    metric_str = str(metric_name)
    standard = standardizer.identify_metric_standard(metric_str)
    
    metric_standards_map[i] = {
        'metric': metric_str[:60],
        'group': metric_group,
        'unit': standard['unit'],
        'direction': standard['direction'],
        'scale': standard['scale']
    }

# Count distributions
unit_counts = defaultdict(int)
direction_counts = defaultdict(int)

for m_info in metric_standards_map.values():
    unit_counts[m_info['unit']] += 1
    direction_counts[m_info['direction']] += 1

print("\nUnit distribution:")
for unit, count in sorted(unit_counts.items(), key=lambda x: -x[1]):
    print(f"  {unit:20s}: {count:3d}")

print("\nDirection distribution:")
for direction, count in sorted(direction_counts.items(), key=lambda x: -x[1]):
    print(f"  {direction:20s}: {count:3d}")

print("\n" + "-" * 100)
print("METRICS BY CATEGORY")
print("-" * 100)

# Show examples by direction type
direction_examples = defaultdict(list)
for idx, m_info in metric_standards_map.items():
    direction_examples[m_info['direction']].append(m_info['metric'])

for direction in ['higher_better', 'lower_better', 'context_dependent']:
    metrics = direction_examples.get(direction, [])
    if metrics:
        print(f"\n{direction.upper()} (n={len(metrics)}):")
        for metric in metrics[:5]:
            print(f"  • {metric}")
        if len(metrics) > 5:
            print(f"  ... and {len(metrics) - 5} more")

print("\n" + "-" * 100)
print("VALUE NORMALIZATION TESTING")
print("-" * 100)

# Test normalization on actual values
test_samples = []
for idx, row in df.iterrows():
    metric_idx = idx
    if metric_idx not in metric_standards_map:
        continue
    
    standard = metric_standards_map[metric_idx]
    
    # Get first 3 non-null values from months
    for month in months[:3]:
        val = row[month]
        if pd.notna(val):
            normalized, flag = standardizer.normalize_value(val, 
                {'unit': standard['unit'], 'direction': standard['direction'], 'scale': standard['scale']})
            test_samples.append({
                'metric': standard['metric'][:40],
                'unit': standard['unit'],
                'direction': standard['direction'],
                'raw_value': val,
                'normalized': normalized,
                'flag': flag
            })
            if len(test_samples) >= 20:
                break
    
    if len(test_samples) >= 20:
        break

print("\nSample normalization results (first 20 values):")
for sample in test_samples:
    status = "✓" if sample['flag'] == 'VALID' else "⚠" if sample['flag'].startswith('SCALED') else "✗"
    print(f"  {status} {sample['metric']:40s} | {sample['direction']:15s} | {str(sample['raw_value']):8s} → {str(sample['normalized'])[:8]:8s}")

print("\n" + "-" * 100)
print("STANDARD DEFINITIONS FOR TIME METRICS")
print("-" * 100)

# Special handling for time metrics
time_metrics = [m for m, info in metric_standards_map.items() if info['unit'] == 'time'][:5]
print(f"\nTime metrics (n={len([m for m, info in metric_standards_map.items() if info['unit'] == 'time'])}):")

if time_metrics:
    print("Sample time metrics:")
    for idx in time_metrics:
        metric_name = df.iloc[idx]['Metric']
        benchmark = df.iloc[idx]['Industry Benchmarks']
        print(f"  • {metric_name}: Benchmark = {benchmark}")

print("\n" + "-" * 100)
print("METRIC GROUP ANALYSIS")
print("-" * 100)

# Group by metric group and show common standards
groups = defaultdict(lambda: defaultdict(int))
for idx, m_info in metric_standards_map.items():
    group = m_info['group']
    unit = m_info['unit']
    direction = m_info['direction']
    groups[group][f"{unit}_{direction}"] += 1

for group_name in sorted([g for g in groups.keys() if pd.notna(g)]):
    print(f"\n{group_name}:")
    for standard, count in sorted(groups[group_name].items(), key=lambda x: -x[1]):
        print(f"  {standard:25s}: {count:2d} metrics")

print("\n" + "-" * 100)
print("STANDARDIZATION COMPLETENESS")
print("-" * 100)

# Check how many metrics have standards assigned
total_metrics = len([m for m in metric_standards_map.values() if m['metric'] != 'nan'])
unknown_count = sum(1 for m in metric_standards_map.values() if m['unit'] == 'unknown')
recognized_count = total_metrics - unknown_count

print(f"\nTotal metrics analyzed: {total_metrics}")
print(f"Recognized standards: {recognized_count} ({recognized_count/total_metrics*100:.1f}%)")
print(f"Unknown/generic: {unknown_count} ({unknown_count/total_metrics*100:.1f}%)")

print("\n" + "=" * 100)
print("END OF ANALYSIS - StandardizerMetric is ready for Phase 0.5")
print("=" * 100)
print("\nKey Findings:")
print("  • Metrics standardized into 3 unit types: %, time, count")
print("  • Direction assigned: higher_better, lower_better, context_dependent")
print("  • Ready to create normalized dataset for trend analysis")
print("  • Benchmark ranges can be applied to normalized values")
