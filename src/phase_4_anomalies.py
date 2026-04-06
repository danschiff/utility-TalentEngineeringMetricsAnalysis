"""Phase 4: Anomaly Detection - Identify unusual patterns and outliers."""

import pandas as pd
import numpy as np
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Load cleaned dataset and trend analysis
cleaned_file = "output/team_metrics_cleaned.csv"
trends_file = "output/trends_analysis.csv"

df = pd.read_csv(cleaned_file)
trends_df = pd.read_csv(trends_file)

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']

print("=" * 100)
print("PHASE 4: ANOMALY DETECTION")
print("=" * 100)

print("\n1. DETECTING ANOMALIES")
print("-" * 100)

anomalies = []

# Type 1: Statistical outliers (values > 2 standard deviations from team mean)
print("  Type 1: Statistical outliers (Z-score > 2)")

for team in df['team'].dropna().unique():
    team_df = df[df['team'] == team]
    
    for idx, row in team_df.iterrows():
        metric_values = []
        for month in months:
            val = row[f'{month}_value']
            if pd.notna(val):
                metric_values.append((val, month))
        
        if len(metric_values) >= 3:
            values = [v[0] for v in metric_values]
            mean = np.mean(values)
            std = np.std(values)
            
            if std > 0:
                for val, month in metric_values:
                    z_score = abs((val - mean) / std)
                    if z_score > 2:
                        anomalies.append({
                            'type': 'Statistical Outlier',
                            'metric': row['metric'],
                            'team': team,
                            'month': month,
                            'value': val,
                            'mean': mean,
                            'severity': z_score,
                            'confidence': 'High' if z_score > 3 else 'Medium'
                        })

# Type 2: Sudden spike/drop (month-over-month change > 50%)
print("  Type 2: Sudden changes (month-over-month > 50%)")

for idx, row in df.iterrows():
    metric_values = []
    for month in months:
        val = row[f'{month}_value']
        metric_values.append((val, month))
    
    for i in range(1, len(metric_values)):
        prev_val, prev_month = metric_values[i-1]
        curr_val, curr_month = metric_values[i]
        
        if pd.notna(prev_val) and pd.notna(curr_val) and prev_val != 0:
            pct_change = abs((curr_val - prev_val) / prev_val)
            
            if pct_change > 0.5:  # 50% change
                anomalies.append({
                    'type': 'Sudden Change',
                    'metric': row['metric'],
                    'team': row['team'],
                    'month': f"{prev_month} → {curr_month}",
                    'value': curr_val,
                    'prev_value': prev_val,
                    'severity': pct_change,
                    'confidence': 'High' if pct_change > 1.0 else 'Medium'
                })

# Type 3: Trend reversal (improving then declining or vice versa)
print("  Type 3: Trend reversals")

for idx, row in trends_df.iterrows():
    # Get values from the original dataframe instead
    metric_name = row['metric']
    team_name = row['team']
    
    original_row = df[(df['metric'] == metric_name) & (df['team'] == team_name)].iloc[0]
    non_null_values = [original_row[f'{m}_value'] for m in months if pd.notna(original_row[f'{m}_value'])]
    
    if len(non_null_values) >= 5:
        # Split into first and second half
        mid = len(non_null_values) // 2
        first_half = non_null_values[:mid]
        second_half = non_null_values[mid:]
        
        if first_half and second_half:
            first_trend = np.mean(second_half) - np.mean(first_half)
            
            # Check if trend reverses within second half
            if len(second_half) >= 3:
                for i in range(1, len(second_half)):
                    if (second_half[i] - second_half[i-1]) * first_trend < 0:
                        anomalies.append({
                            'type': 'Trend Reversal',
                            'metric': row['metric'],
                            'team': row['team'],
                            'month': 'Mid-period',
                            'value': None,
                            'severity': abs(first_trend),
                            'confidence': 'Medium'
                        })
                        break

# Type 4: Unusually stable (near-zero variance - might indicate no tracking)
print("  Type 4: Unusually stable metrics")

for idx, row in df.iterrows():
    metric_values = [row[f'{m}_value'] for m in months if pd.notna(row[f'{m}_value'])]
    
    if len(metric_values) >= 6:
        std = np.std(metric_values)
        mean = np.mean(metric_values)
        
        # If std is very low but not zero, might be a concern
        if 0 < std < 0.01 * abs(mean) and abs(mean) > 0:
            anomalies.append({
                'type': 'Unusually Stable',
                'metric': row['metric'],
                'team': row['team'],
                'month': 'All months',
                'value': mean,
                'severity': std,
                'confidence': 'Low'  # Could be legitimate
            })

anomaly_df = pd.DataFrame(anomalies)

print(f"Total anomalies detected: {len(anomaly_df)}")

if len(anomaly_df) > 0:
    anomaly_type_counts = anomaly_df['type'].value_counts()
    print("\nAnomalies by type:")
    for atype, count in anomaly_type_counts.items():
        print(f"  {atype:25s}: {count:3d}")
    
    severity_counts = anomaly_df['confidence'].value_counts()
    print("\nAnomalies by confidence:")
    for conf, count in severity_counts.items():
        print(f"  {conf:10s}: {count:3d}")

print("\n2. ANOMALIES BY TEAM")
print("-" * 100)

if len(anomaly_df) > 0:
    team_anomalies = anomaly_df.groupby('team').size().sort_values(ascending=False)
    for team, count in team_anomalies.items():
        print(f"  {team:35s}: {count:3d} anomalies")

print("\n3. HIGH-CONFIDENCE ANOMALIES (Suspicious)")
print("-" * 100)

if len(anomaly_df) > 0:
    high_conf = anomaly_df[anomaly_df['confidence'] == 'High'].sort_values('severity', ascending=False)
    
    if len(high_conf) > 0:
        print(f"\nTotal high-confidence anomalies: {len(high_conf)}\n")
        
        print("Statistical Outliers:")
        stat_outliers = high_conf[high_conf['type'] == 'Statistical Outlier'].head(10)
        for idx, row in stat_outliers.iterrows():
            print(f"  • {row['metric'][:45]:45s} | {row['team']:25s} | {row['month']:12s}")
            print(f"    Value: {row['value']:.2f}, Z-score: {row['severity']:.2f}")
        
        print("\nSudden Changes:")
        sudden = high_conf[high_conf['type'] == 'Sudden Change'].head(10)
        for idx, row in sudden.iterrows():
            pct = row['severity'] * 100
            print(f"  • {row['metric'][:45]:45s} | {row['team']:25s}")
            print(f"    {row['month']:40s} Change: {pct:+7.1f}%")

print("\n4. ANOMALY INVESTIGATION GUIDANCE")
print("-" * 100)

if len(anomaly_df) > 0:
    # Find metrics with multiple types of anomalies
    metric_anomaly_counts = anomaly_df.groupby('metric').size().sort_values(ascending=False)
    
    print(f"\nMetrics with multiple anomalies (investigate first):")
    for metric, count in metric_anomaly_counts.head(10).items():
        metric_data = anomaly_df[anomaly_df['metric'] == metric]
        types = ', '.join(metric_data['type'].unique())
        print(f"  • {metric[:50]:50s}")
        print(f"    {count} anomalies ({types})")

print("\n5. ANOMALY SEVERITY SCORE")
print("-" * 100)

if len(anomaly_df) > 0:
    # Create severity score combining type and confidence
    def get_severity_score(row):
        type_weights = {
            'Statistical Outlier': 3,
            'Sudden Change': 2,
            'Trend Reversal': 1.5,
            'Unusually Stable': 0.5
        }
        confidence_weights = {
            'High': 1.0,
            'Medium': 0.7,
            'Low': 0.3
        }
        
        type_score = type_weights.get(row['type'], 1)
        conf_score = confidence_weights.get(row['confidence'], 0.5)
        
        return (type_score * conf_score * (row['severity'] + 1))
    
    anomaly_df['severity_score'] = anomaly_df.apply(get_severity_score, axis=1)
    
    top_anomalies = anomaly_df.nlargest(15, 'severity_score')
    
    print("\nTop 15 Most Concerning Anomalies:\n")
    for idx, (i, row) in enumerate(top_anomalies.iterrows(), 1):
        print(f"{idx:2d}. [{row['type']:20s}] {row['metric'][:45]:45s}")
        print(f"    Team: {row['team']}, Month: {row['month']}, Confidence: {row['confidence']}")
        print(f"    Severity Score: {row['severity_score']:.2f}\n")

print("\n6. ANOMALY EXPORT")
print("-" * 100)

if len(anomaly_df) > 0:
    # Save all anomalies
    anomaly_df.to_csv('output/anomalies_all.csv', index=False)
    print(f"✓ All anomalies saved to: output/anomalies_all.csv ({len(anomaly_df)} records)")
    
    # Save high-confidence only
    high_conf_df = anomaly_df[anomaly_df['confidence'] == 'High']
    if len(high_conf_df) > 0:
        high_conf_df.to_csv('output/anomalies_high_confidence.csv', index=False)
        print(f"✓ High-confidence anomalies saved to: output/anomalies_high_confidence.csv ({len(high_conf_df)} records)")

print("\n" + "=" * 100)
print("PHASE 4 COMPLETE - Anomaly Detection Finished")
print("=" * 100)

print("\nSummary:")
if len(anomaly_df) > 0:
    print(f"  • {len(anomaly_df)} total anomalies detected")
    print(f"  • {len(anomaly_df[anomaly_df['confidence'] == 'High'])} high-confidence anomalies")
    print(f"  • {len(anomaly_df['metric'].unique())} unique metrics with anomalies")
    print(f"  • {len(anomaly_df['team'].unique())} teams affected")
else:
    print("  • No anomalies detected with current thresholds")

print("\nNext Steps:")
print("  • Review high-confidence anomalies in: output/anomalies_high_confidence.csv")
print("  • Investigate metrics with multiple anomaly types")
print("  • Correlate anomalies with business events or changes")
print("  • Use trend data to understand context: output/trends_analysis.csv")
