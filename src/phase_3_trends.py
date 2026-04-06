"""Phase 3: Trend Visualization - Create charts showing metric trends over time."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load cleaned dataset
cleaned_file = "output/team_metrics_cleaned.csv"
df = pd.read_csv(cleaned_file)

months = ['July', 'August', 'September', 'October', 'November', 'December', 
          'January', 'February', 'March']
# Month order for plotting (Jul-Mar)
month_order = list(range(len(months)))

print("=" * 100)
print("PHASE 3: TREND VISUALIZATION")
print("=" * 100)

print("\n1. PREPARING TREND DATA")
print("-" * 100)

# Create trend-ready dataset (metrics with 6+ months of data)
trend_data = []
for idx, row in df.iterrows():
    months_with_data = sum(1 for m in months if pd.notna(row[f'{m}_value']))
    
    if months_with_data >= 6:  # At least 6 months for meaningful trend
        values = [row[f'{m}_value'] for m in months]
        
        # Calculate trend statistics
        non_null_indices = [i for i, v in enumerate(values) if pd.notna(v)]
        non_null_values = [v for v in values if pd.notna(v)]
        
        if len(non_null_values) >= 3:
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(non_null_indices, non_null_values)
            
            # Trend direction
            if abs(slope) < 0.1:
                trend_dir = 'Stable'
            elif slope > 0:
                trend_dir = 'Improving' if row['metric_direction'] == 'higher_better' else 'Declining'
            else:
                trend_dir = 'Declining' if row['metric_direction'] == 'higher_better' else 'Improving'
            
            # Percent change first to last
            first_val = non_null_values[0]
            last_val = non_null_values[-1]
            pct_change = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            
            trend_data.append({
                'metric': row['metric'],
                'team': row['team'],
                'metric_group': row['metric_group'],
                'direction': row['metric_direction'],
                'values': values,
                'slope': slope,
                'pct_change': pct_change,
                'trend': trend_dir,
                'r_squared': r_value ** 2,
                'months_data': months_with_data
            })

trend_df = pd.DataFrame(trend_data)
print(f"Metrics with trend data: {len(trend_df)}")

# Analyze trends
trend_counts = trend_df['trend'].value_counts()
print("\nTrend directions:")
for trend, count in trend_counts.items():
    print(f"  {trend:12s}: {count:3d} metrics ({count/len(trend_df)*100:5.1f}%)")

print("\n2. MOST IMPROVED METRICS (Top 10)")
print("-" * 100)

most_improved = trend_df[trend_df['trend'].isin(['Improving'])].nlargest(10, 'pct_change')
for idx, row in most_improved.iterrows():
    print(f"  {row['metric'][:50]:50s} | {row['pct_change']:+7.1f}% | {row['team']}")

print("\n3. MOST DECLINING METRICS (Top 10)")
print("-" * 100)

most_declining = trend_df[trend_df['trend'].isin(['Declining'])].nsmallest(10, 'pct_change')
for idx, row in most_declining.iterrows():
    print(f"  {row['metric'][:50]:50s} | {row['pct_change']:+7.1f}% | {row['team']}")

print("\n4. GENERATING VISUALIZATIONS")
print("-" * 100)

# Create output directory if needed
import os
os.makedirs('output', exist_ok=True)

# Visualization 1: Sample trend lines (top metrics)
print("  Creating visualization 1: Sample trend lines...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Sample Metric Trends: July - March', fontsize=16, fontweight='bold')

# Select 4 interesting metrics
sample_metrics = [
    trend_df[trend_df['trend'] == 'Improving'].iloc[0] if len(trend_df[trend_df['trend'] == 'Improving']) > 0 else None,
    trend_df[trend_df['trend'] == 'Declining'].iloc[0] if len(trend_df[trend_df['trend'] == 'Declining']) > 0 else None,
    trend_df[trend_df['trend'] == 'Stable'].iloc[0] if len(trend_df[trend_df['trend'] == 'Stable']) > 0 else None,
    trend_df.iloc[0],
]

sample_metrics = [m for m in sample_metrics if m is not None][:4]

for ax_idx, (ax, metric) in enumerate(zip(axes.flat, sample_metrics)):
    values = metric['values']
    x_pos = list(range(len(months)))
    
    # Plot data
    ax.plot(x_pos, values, 'o-', linewidth=2, markersize=8, label='Actual', alpha=0.8)
    
    # Plot trend line
    non_null_indices = [i for i, v in enumerate(values) if pd.notna(v)]
    non_null_values = [v for v in values if pd.notna(v)]
    
    if len(non_null_values) >= 2:
        z = np.polyfit(non_null_indices, non_null_values, 1)
        p = np.poly1d(z)
        trend_line = [p(i) for i in x_pos]
        ax.plot(x_pos, trend_line, '--', linewidth=2, label='Trend', alpha=0.6)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(months, rotation=45, ha='right')
    ax.set_title(f"{metric['metric'][:40]}\n{metric['trend']} ({metric['pct_change']:+.1f}%)", fontsize=11, fontweight='bold')
    ax.set_ylabel('Value')
    ax.grid(True, alpha=0.3)
    ax.legend()

plt.tight_layout()
plt.savefig('output/trend_samples.png', dpi=100, bbox_inches='tight')
print("    ✓ Saved: trend_samples.png")
plt.close()

# Visualization 2: Trend distribution by team
print("  Creating visualization 2: Trends by team...")

fig, ax = plt.subplots(figsize=(12, 6))

teams = sorted(trend_df['team'].dropna().unique())
trend_types = ['Improving', 'Stable', 'Declining']
x_pos = np.arange(len(teams))
width = 0.25

for i, trend_type in enumerate(trend_types):
    counts = [len(trend_df[(trend_df['team'] == team) & (trend_df['trend'] == trend_type)]) for team in teams]
    ax.bar(x_pos + i*width, counts, width, label=trend_type)

ax.set_xlabel('Team', fontweight='bold')
ax.set_ylabel('Number of Metrics', fontweight='bold')
ax.set_title('Trend Distribution by Team', fontsize=14, fontweight='bold')
ax.set_xticks(x_pos + width)
ax.set_xticklabels(teams, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output/trends_by_team.png', dpi=100, bbox_inches='tight')
print("    ✓ Saved: trends_by_team.png")
plt.close()

# Visualization 3: Scatter plot - Percent change vs R-squared
print("  Creating visualization 3: Trend strength vs magnitude...")

fig, ax = plt.subplots(figsize=(12, 7))

colors = {'Improving': 'green', 'Stable': 'gray', 'Declining': 'red'}
for trend_type in ['Declining', 'Stable', 'Improving']:
    data = trend_df[trend_df['trend'] == trend_type]
    ax.scatter(data['r_squared'], data['pct_change'], 
              label=trend_type, s=100, alpha=0.6, color=colors[trend_type])

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.axvline(x=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Moderate trend strength')

ax.set_xlabel('Trend Strength (R²)', fontweight='bold', fontsize=11)
ax.set_ylabel('Percent Change (Jul-Mar)', fontweight='bold', fontsize=11)
ax.set_title('Metric Trend Strength vs Magnitude of Change', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Add reference zones
ax.text(0.75, 20, 'Strong\nImprovement', ha='center', fontsize=9, alpha=0.5, bbox=dict(boxstyle='round', facecolor='green', alpha=0.1))
ax.text(0.75, -20, 'Strong\nDecline', ha='center', fontsize=9, alpha=0.5, bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))

plt.tight_layout()
plt.savefig('output/trend_strength_vs_magnitude.png', dpi=100, bbox_inches='tight')
print("    ✓ Saved: trend_strength_vs_magnitude.png")
plt.close()

# Visualization 4: Metric group trends
print("  Creating visualization 4: Trends by metric group...")

fig, ax = plt.subplots(figsize=(12, 6))

groups = sorted(trend_df['metric_group'].dropna().unique())
trend_types = ['Improving', 'Stable', 'Declining']
x_pos = np.arange(len(groups))
width = 0.25

for i, trend_type in enumerate(trend_types):
    counts = [len(trend_df[(trend_df['metric_group'] == group) & (trend_df['trend'] == trend_type)]) for group in groups]
    ax.bar(x_pos + i*width, counts, width, label=trend_type)

ax.set_xlabel('Metric Group', fontweight='bold')
ax.set_ylabel('Number of Metrics', fontweight='bold')
ax.set_title('Trend Distribution by Metric Group', fontsize=14, fontweight='bold')
ax.set_xticks(x_pos + width)
ax.set_xticklabels(groups, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output/trends_by_metric_group.png', dpi=100, bbox_inches='tight')
print("    ✓ Saved: trends_by_metric_group.png")
plt.close()

# Visualization 5: Heatmap of team performance over time
print("  Creating visualization 5: Team performance heatmap...")

# Create aggregated data by team and month (average values)
heatmap_data = {}
for team in sorted(trend_df['team'].dropna().unique()):
    team_metrics = trend_df[trend_df['team'] == team]
    monthly_avg = []
    for month in months:
        values = []
        for idx, metric in team_metrics.iterrows():
            val = metric['values'][months.index(month)]
            if pd.notna(val):
                # Normalize direction
                if metric['direction'] == 'lower_better':
                    val = -val
                values.append(val)
        monthly_avg.append(np.mean(values) if values else np.nan)
    heatmap_data[team] = monthly_avg

heatmap_df = pd.DataFrame(heatmap_data, index=months).T

fig, ax = plt.subplots(figsize=(13, 7))
sns.heatmap(heatmap_df, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
           cbar_kws={'label': 'Direction-adjusted Avg Value'}, ax=ax)
ax.set_title('Team Performance Over Time (Normalized Trends)', fontsize=14, fontweight='bold')
ax.set_xlabel('Month', fontweight='bold')
ax.set_ylabel('Team', fontweight='bold')

plt.tight_layout()
plt.savefig('output/team_performance_heatmap.png', dpi=100, bbox_inches='tight')
print("    ✓ Saved: team_performance_heatmap.png")
plt.close()

print("\n5. TREND SUMMARY STATISTICS")
print("-" * 100)

print(f"\nTotal analyzed metrics: {len(trend_df)}")
print(f"  Improving: {len(trend_df[trend_df['trend'] == 'Improving'])} ({len(trend_df[trend_df['trend'] == 'Improving'])/len(trend_df)*100:.1f}%)")
print(f"  Stable: {len(trend_df[trend_df['trend'] == 'Stable'])} ({len(trend_df[trend_df['trend'] == 'Stable'])/len(trend_df)*100:.1f}%)")
print(f"  Declining: {len(trend_df[trend_df['trend'] == 'Declining'])} ({len(trend_df[trend_df['trend'] == 'Declining'])/len(trend_df)*100:.1f}%)")

print(f"\nChange statistics (Jul to Mar):")
print(f"  Avg change: {trend_df['pct_change'].mean():+.1f}%")
print(f"  Max improvement: {trend_df['pct_change'].max():+.1f}%")
print(f"  Max decline: {trend_df['pct_change'].min():+.1f}%")

print(f"\nTrend strength (R² values):")
print(f"  Mean R²: {trend_df['r_squared'].mean():.3f}")
print(f"  Strong trends (R² > 0.7): {len(trend_df[trend_df['r_squared'] > 0.7])}")
print(f"  Weak trends (R² < 0.3): {len(trend_df[trend_df['r_squared'] < 0.3])}")

# Save trend data for Phase 4
trend_df.to_csv('output/trends_analysis.csv', index=False)
print(f"\nTrend analysis saved to: output/trends_analysis.csv")

print("\n" + "=" * 100)
print("PHASE 3 COMPLETE - Visualizations Generated")
print("=" * 100)

print("\nGenerated visualizations:")
print("  1. trend_samples.png - Sample 4 metric trends (improving/declining/stable)")
print("  2. trends_by_team.png - Distribution of trend types per team")
print("  3. trend_strength_vs_magnitude.png - Trend strength vs % change scatter")
print("  4. trends_by_metric_group.png - Distribution of trends by metric group")
print("  5. team_performance_heatmap.png - Team performance across all months")

print("\nNext Phase: Phase 4 - Anomaly Detection")
