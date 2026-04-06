"""Task 0.3: Extract numeric values from percentages and ranges."""

import pandas as pd
import numpy as np
import re
from typing import Tuple, Optional, Dict, List
from collections import defaultdict

excel_file = "input/Talent Engineering Metrics.xlsx"

# Load the Team-Level Template sheet
df = pd.read_excel(excel_file, sheet_name="Team-Level Template")


class BenchmarkParser:
    """Parser for benchmark ranges and percentages."""
    
    def __init__(self):
        self.parse_stats = {
            'single_number': 0,
            'range_parsed': 0,
            'percentage': 0,
            'with_units': 0,
            'tbd': 0,
            'empty': 0,
            'other': 0,
        }
        self.benchmark_formats = defaultdict(int)
    
    def parse_benchmark(self, val) -> Dict:
        """
        Parse a benchmark value and extract min, max, midpoint, and units.
        
        Returns:
            {
                'raw': original_value,
                'min': lower_bound or single_value,
                'max': upper_bound or None,
                'midpoint': average,
                'unit': extracted unit,
                'type': 'single', 'range', 'percentage', 'tbd', 'empty'
            }
        """
        result = {
            'raw': str(val) if not pd.isna(val) else None,
            'min': None,
            'max': None,
            'midpoint': None,
            'unit': None,
            'type': 'empty'
        }
        
        # Handle null/NaN
        if pd.isna(val):
            self.parse_stats['empty'] += 1
            return result
        
        val_str = str(val).strip()
        
        # Handle empty string
        if val_str == "" or val_str.lower() == "nan":
            self.parse_stats['empty'] += 1
            return result
        
        # Handle TBD or similar
        if val_str.upper() in ['TBD', 'N/A', 'NA', 'NONE']:
            result['type'] = 'tbd'
            self.parse_stats['tbd'] += 1
            self.benchmark_formats[val_str.upper()] += 1
            return result
        
        # Extract unit (%, days, hours, month, weeks, etc.)
        unit_match = re.search(r'(days?|hours?|weeks?|month|months|/|PDR|%)', val_str, re.IGNORECASE)
        if unit_match:
            result['unit'] = unit_match.group().lower()
        
        # Try to extract numbers with range operator (– or -)
        range_patterns = [
            r'(\d+\.?\d*)\s*–\s*(\d+\.?\d*)',  # en-dash with decimals
            r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',   # hyphen with decimals
            r'(\d+)\s*to\s*(\d+)',              # 'to' pattern
        ]
        
        for pattern in range_patterns:
            range_match = re.search(pattern, val_str, re.IGNORECASE)
            if range_match:
                try:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    result['min'] = min_val
                    result['max'] = max_val
                    result['midpoint'] = (min_val + max_val) / 2
                    result['type'] = 'range'
                    self.parse_stats['range_parsed'] += 1
                    self.benchmark_formats[f'range_{result["unit"]}'] += 1
                    return result
                except ValueError:
                    pass
        
        # Try to extract single number
        single_number_match = re.search(r'(\d+\.?\d*)', val_str)
        if single_number_match:
            try:
                num = float(single_number_match.group(1))
                result['min'] = num
                result['max'] = None
                result['midpoint'] = num
                
                if '%' in val_str:
                    result['type'] = 'percentage'
                    self.parse_stats['percentage'] += 1
                    self.benchmark_formats['percentage'] += 1
                elif result['unit']:
                    result['type'] = 'with_units'
                    self.parse_stats['with_units'] += 1
                    self.benchmark_formats[f'single_{result["unit"]}'] += 1
                else:
                    result['type'] = 'single_number'
                    self.parse_stats['single_number'] += 1
                    self.benchmark_formats['single_number'] += 1
                return result
            except ValueError:
                pass
        
        # If we get here, couldn't parse
        result['type'] = 'other'
        self.parse_stats['other'] += 1
        self.benchmark_formats['unparseable'] += 1
        return result


print("=" * 100)
print("TASK 0.3: EXTRACT NUMERIC FROM PERCENTAGES AND RANGES")
print("=" * 100)

parser = BenchmarkParser()

# Parse Industry Benchmarks column
print("\nParsing Industry Benchmarks column:")
print("-" * 100)

benchmarks_parsed = []
for i, val in enumerate(df['Industry Benchmarks']):
    parsed = parser.parse_benchmark(val)
    parsed['row_idx'] = i
    benchmarks_parsed.append(parsed)

# Count by type
type_counts = defaultdict(int)
for parsed in benchmarks_parsed:
    type_counts[parsed['type']] += 1

print("Parse type distribution:")
for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {ptype:15s}: {count:3d}")

print(f"\nBenchmark format examples found:")
print("-" * 100)
for fmt, count in sorted(parser.benchmark_formats.items(), key=lambda x: -x[1])[:15]:
    print(f"  {fmt:25s}: {count:3d}")

print("\n" + "-" * 100)
print("SAMPLE PARSED BENCHMARKS")
print("-" * 100)

# Show examples of each parse type
for ptype in ['single_number', 'range', 'percentage', 'with_units', 'tbd', 'other']:
    examples = [p for p in benchmarks_parsed if p['type'] == ptype][:3]
    if examples:
        print(f"\n{ptype.upper()}:")
        for ex in examples:
            if ex['max'] is not None:
                print(f"  Raw: '{ex['raw']}' → Min: {ex['min']}, Max: {ex['max']}, Mid: {ex['midpoint']}, Unit: {ex['unit']}")
            else:
                print(f"  Raw: '{ex['raw']}' → Value: {ex['min']}, Unit: {ex['unit']}")

print("\n" + "-" * 100)
print("METRICS WITH BENCHMARKS")
print("-" * 100)

# Show which metrics have what type of benchmarks
benchmark_by_metric = []
for i, row in df.iterrows():
    parsed = benchmarks_parsed[i]
    if parsed['type'] not in ['empty', 'tbd']:
        benchmark_by_metric.append({
            'metric': str(row['Metric'])[:50],
            'team': row['Team'],
            'benchmark_type': parsed['type'],
            'range': f"{parsed['min']} - {parsed['max']}" if parsed['max'] else str(parsed['min']),
            'unit': parsed['unit']
        })

if benchmark_by_metric:
    print(f"\nTotal metrics with benchmarks: {len(benchmark_by_metric)}")
    print("\nFirst 15 metrics with benchmarks:")
    for item in benchmark_by_metric[:15]:
        print(f"  • {item['metric']:45s} | {item['benchmark_type']:15s} | {item['range']:15s} {item['unit'] or ''}")

print("\n" + "-" * 100)
print("BENCHMARK STATISTICS")
print("-" * 100)

# Get only range benchmarks for statistics
range_benchmarks = [p for p in benchmarks_parsed if p['type'] == 'range']

if range_benchmarks:
    midpoints = [p['midpoint'] for p in range_benchmarks if p['midpoint'] is not None]
    ranges_widths = [p['max'] - p['min'] for p in range_benchmarks if p['max'] and p['min']]
    
    print(f"\nRange benchmarks statistics (n={len(range_benchmarks)}):")
    print(f"  Midpoint - Min: {np.min(midpoints):.2f}, Max: {np.max(midpoints):.2f}, Mean: {np.mean(midpoints):.2f}")
    print(f"  Range width - Min: {np.min(ranges_widths):.2f}, Max: {np.max(ranges_widths):.2f}, Mean: {np.mean(ranges_widths):.2f}")

print("\n" + "-" * 100)
print("PARSING STATISTICS")
print("-" * 100)

for stat_type, count in sorted(parser.parse_stats.items(), key=lambda x: -x[1]):
    total = sum(parser.parse_stats.values())
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {stat_type:20s}: {count:3d} ({pct:5.1f}%)")

print("\n" + "=" * 100)
print("END OF ANALYSIS - BenchmarkParser is ready for Phase 0.4")
print("=" * 100)
