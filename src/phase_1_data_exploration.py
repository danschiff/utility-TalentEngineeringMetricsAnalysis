"""Phase 1: Data Loading & Exploration - Validate and explore cleaned data."""

import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned dataset
cleaned_file = "output/team_metrics_cleaned.csv"
df = pd.read_csv(cleaned_file)

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']

print("=" * 100)
print("PHASE 1: DATA LOADING & EXPLORATION")
print("=" * 100)

print("\n1. DATASET OVERVIEW")
print("-" * 100)
print(f"Shape: {df.shape[0]} metrics × {df.shape[1]} columns")
print(f"Teams: {df['team'].nunique()}")
print(f"Metric Groups: {df['metric_group'].nunique()}")
print(f"Data Sources: {df['source'].nunique()}")

print("\n2. DATA QUALITY VALIDATION")
print("-" * 100)

# Check for nulls in metadata
metadata_nulls = {col: df[col].isna().sum() for col in ['team', 'metric', 'metric_group', 'source']}
print("Metadata completeness:")
for col, nulls in metadata_nulls.items():
    print(f"  {col:20s}: {nulls} nulls ({(1 - nulls/len(df))*100:.1f}% complete)")

# Check benchmark columns
benchmark_complete = sum(1 for v in df['benchmark_mid'] if pd.notna(v))
print(f"\nBenchmark data: {benchmark_complete} metrics have benchmarks ({benchmark_complete/len(df)*100:.1f}%)")

print("\n3. DATA COMPLETENESS BY TEAM")
print("-" * 100)

team_stats = []
for team in sorted(df['team'].dropna().unique()):
    team_df = df[df['team'] == team]
    
    # Count total data points possible
    total_slots = len(team_df) * len(months)
    
    # Count actual values
    actual_values = sum([sum(1 for v in team_df[f'{m}_value'] if pd.notna(v)) for m in months])
    
    # Count metrics with at least 1 value
    metrics_with_data = sum(1 for idx, row in team_df.iterrows() 
                            if any(pd.notna(row[f'{m}_value']) for m in months))
    
    completeness = actual_values / total_slots * 100 if total_slots > 0 else 0
    
    team_stats.append({
        'team': team,
        'metrics': len(team_df),
        'metrics_with_data': metrics_with_data,
        'data_slots_filled': actual_values,
        'total_slots': total_slots,
        'completeness_%': completeness
    })

for stat in sorted(team_stats, key=lambda x: -x['completeness_%']):
    print(f"  {stat['team']:35s}: {stat['completeness_%']:5.1f}% "
          f"({stat['metrics_with_data']}/{stat['metrics']} metrics have data)")

print("\n4. DATA COMPLETENESS BY MONTH")
print("-" * 100)

month_stats = []
for month in months:
    values = df[f'{month}_value']
    non_null = sum(1 for v in values if pd.notna(v))
    completeness = non_null / len(df) * 100
    
    month_stats.append({
        'month': month,
        'values': non_null,
        'pct_complete': completeness
    })
    
    bar = '█' * int(completeness / 5) + '░' * (20 - int(completeness / 5))
    print(f"  {month:12s}: {non_null:3d} values ({completeness:5.1f}%) {bar}")

print("\n5. DATA COMPLETENESS BY METRIC GROUP")
print("-" * 100)

group_stats = []
for group in sorted(df['metric_group'].dropna().unique()):
    group_df = df[df['metric_group'] == group]
    
    total_slots = len(group_df) * len(months)
    actual_values = sum([sum(1 for v in group_df[f'{m}_value'] if pd.notna(v)) for m in months])
    completeness = actual_values / total_slots * 100 if total_slots > 0 else 0
    
    group_stats.append({
        'group': group,
        'metrics': len(group_df),
        'completeness_%': completeness
    })

for stat in sorted(group_stats, key=lambda x: -x['completeness_%']):
    print(f"  {stat['group']:35s}: {stat['completeness_%']:5.1f}% ({stat['metrics']} metrics)")

print("\n6. METRICS READY FOR TREND ANALYSIS")
print("-" * 100)

# Identify metrics with 6+ months of data (can show trend)
trend_ready = []
for idx, row in df.iterrows():
    months_with_data = sum(1 for m in months if pd.notna(row[f'{m}_value']))
    if months_with_data >= 6:
        trend_ready.append({
            'metric': row['metric'],
            'team': row['team'],
            'group': row['metric_group'],
            'months_data': months_with_data,
            'direction': row['metric_direction'],
            'benchmark': row['benchmark_mid']
        })

print(f"Metrics with 6+ months of data: {len(trend_ready)} ({len(trend_ready)/len(df)*100:.1f}%)")
print(f"Metrics with 9 months (complete): {sum(1 for t in trend_ready if t['months_data'] == 9)}")

if trend_ready:
    print("\nSample trend-ready metrics:")
    for metric in trend_ready[:10]:
        bench_str = f" | Bench: {metric['benchmark']:.1f}" if pd.notna(metric['benchmark']) else ""
        print(f"  • {metric['metric'][:45]:45s} | {metric['months_data']} months{bench_str}")

print("\n7. DATA SOURCE DISTRIBUTION")
print("-" * 100)

source_stats = df['source'].value_counts().fillna('Unknown')
for source, count in source_stats.items():
    print(f"  {source:20s}: {count:3d} metrics ({count/len(df)*100:5.1f}%)")

print("\n8. METRIC DIRECTION DISTRIBUTION")
print("-" * 100)

direction_stats = df['metric_direction'].value_counts()
for direction, count in direction_stats.items():
    print(f"  {direction:20s}: {count:3d} metrics ({count/len(df)*100:5.1f}%)")

print("\n9. DATA QUALITY FLAG ANALYSIS")
print("-" * 100)

# Analyze data quality flags
all_flags = defaultdict(int)
for month in months:
    for flag in df[f'{month}_flag']:
        if pd.notna(flag):
            all_flags[flag] += 1

print("Data quality flags found:")
for flag, count in sorted(all_flags.items(), key=lambda x: -x[1]):
    print(f"  {flag:20s}: {count:4d}")

print("\n10. BENCHMARK VS ACTUAL ANALYSIS")
print("-" * 100)

# Compare actual values to benchmarks
comparison_data = []
for idx, row in df.iterrows():
    if pd.notna(row['benchmark_mid']):
        # Get latest non-null value (start with March, work backward)
        latest_value = None
        for month in reversed(months):
            val = row[f'{month}_value']
            if pd.notna(val):
                latest_value = val
                break
        
        if latest_value is not None:
            bench = row['benchmark_mid']
            direction = row['metric_direction']
            
            # Determine if above/below/within benchmark
            if direction == 'higher_better':
                if latest_value >= bench * 1.05:  # 5% buffer
                    status = 'ABOVE'
                elif latest_value <= bench * 0.95:
                    status = 'BELOW'
                else:
                    status = 'WITHIN'
            elif direction == 'lower_better':
                if latest_value <= bench * 0.95:
                    status = 'ABOVE'
                elif latest_value >= bench * 1.05:
                    status = 'BELOW'
                else:
                    status = 'WITHIN'
            else:
                status = 'CONTEXT'
            
            comparison_data.append({
                'metric': row['metric'],
                'team': row['team'],
                'actual': latest_value,
                'benchmark': bench,
                'variance_%': ((latest_value - bench) / bench * 100) if bench != 0 else 0,
                'status': status
            })

if comparison_data:
    comparison_df = pd.DataFrame(comparison_data)
    print(f"Metrics with benchmark comparisons: {len(comparison_df)}")
    
    status_counts = comparison_df['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status:10s}: {count:3d} metrics")
    
    print("\nMetrics BELOW benchmark (opportunity areas):")
    below = comparison_df[comparison_df['status'] == 'BELOW'].sort_values('variance_%')
    for _, row in below.head(5).iterrows():
        print(f"  • {row['metric'][:50]:50s} | {row['variance_%']:+6.1f}%")
    
    print("\nMetrics ABOVE benchmark (strong performers):")
    above = comparison_df[comparison_df['status'] == 'ABOVE'].sort_values('variance_%', ascending=False)
    for _, row in above.head(5).iterrows():
        print(f"  • {row['metric'][:50]:50s} | {row['variance_%']:+6.1f}%")

print("\n11. ANALYSIS READINESS SUMMARY")
print("-" * 100)

ready_checks = {
    'All metadata present': sum(1 for _, row in df.iterrows() if pd.notna(row['team']) and pd.notna(row['metric'])) == len(df),
    'Data for Jul-Feb': all(sum(1 for v in df[f'{m}_value'] if pd.notna(v)) > 100 for m in ['July', 'August', 'September', 'October', 'November', 'December', 'January', 'February']),
    'Trend-ready metrics': len(trend_ready) > 100,
    'Benchmarks available': benchmark_complete > 100,
    'Metrics classified': df['metric_direction'].notna().sum() == len(df),
    'Data flags present': all(df[f'{m}_flag'].notna().sum() > 0 for m in months),
}

readiness_pct = sum(1 for v in ready_checks.values() if v) / len(ready_checks) * 100

for check, status in ready_checks.items():
    status_str = "✓" if status else "✗"
    print(f"  {status_str} {check}")

print(f"\nOverall Readiness: {readiness_pct:.0f}%")

print("\n" + "=" * 100)
print("PHASE 1 COMPLETE - Ready for Phase 2")
print("=" * 100)

print("\nKey Findings:")
print(f"  • {len(trend_ready)} metrics ready for trend analysis")
print(f"  • {len(comparison_df)} metrics can be compared to benchmarks")
print(f"  • July-February period has sufficient data ({sum(s['values'] for s in month_stats[:-1]):.0f} total values)")
print(f"  • March has sparse data ({month_stats[-1]['values']} values) - use with caution")

print("\nNext Phase:")
print("  Phase 2: Benchmark Comparison Analysis")
print("  Phase 3: Trend Visualization")
print("  Phase 4: Anomaly Detection")
