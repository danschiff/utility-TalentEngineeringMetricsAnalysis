# Talent Engineering Metrics Analysis Plan - UPDATED

## Project Goal
Analyze Talent Engineering Metrics from the Team-Level Template worksheet to visualize trends over time and identify patterns or anomalies across 9 teams and 37 metrics.

## Data Overview
**Source:** Team-Level Template worksheet (293 metrics × 18 columns)
- **Teams:** 8 (Employee Voice, Compensation Management, Recognition & Rewards, Onboarding, Learning Management, Performance Management, Recruiting Modernization, Recruiting Innovation)
- **Metric Groups:** 6 (Delivery & Commitments, Quality, Sentiment & Team Health, Productivity & Capacity, Reliability)
- **Data Sources:** Jellyfish (144), JIRA (24), Datadog (32), TBD (64)
- **Time Period:** July through June (fiscal year)
- **Data Quality:** Mixed types in month columns, 93-100% nulls in April-June, extensive nulls throughout

## Implementation Phases

### Phase 0: Data Cleaning & Type Conversion ⚠️ CRITICAL
**Objective:** Transform raw data into analyzable format

**Tasks:**
- Parse month columns from string/object to numeric values
- Handle mixed data types (numbers, percentages, ranges, text)
- Extract numeric values from cells like "80 – 85%" → 80-85 range
- Convert metric values to standardized units
- Identify and handle data entry inconsistencies
- Create clean dataset with proper datetime indexing
- Document data transformation rules for reproducibility

**Special Handling:**
- Percentage metrics: Extract numeric value, store unit separately
- Range values: Store min, max, and midpoint
- Daily/hourly metrics: Convert to standard units (hours, days)
- Missing data: Distinguish between "no data collected" vs. "metric not applicable"

**Deliverable:** Cleaned CSV with numeric time-series data ready for analysis

---

### Phase 1: Data Loading & Exploration (REVISED)
**Objective:** Validate data integrity and understand metric compositions

**Tasks:**
- Load cleaned team-level data
- Validate data quality after transformation
- Analyze data completeness by team and metric group
- Identify metrics with sufficient data for trend analysis (min 6+ months)
- Discovery of valid analysis periods (July-March has good coverage)
- Map benchmark values to actual metrics

**Metrics to Track:**
- Data completeness % by team
- Coverage timeline per metric
- Distribution of data sources

**Deliverable:** Data quality report and analysis readiness assessment

---

### Phase 2: Benchmark Comparison Analysis
**Objective:** Compare actual performance against industry benchmarks

**Tasks:**
- Parse industry benchmark ranges
- Compare team metrics against benchmarks
- Identify metrics above/below/within benchmark range
- Calculate variance from benchmark midpoint
- Rank teams by performance vs. benchmark

**Visualization:**
- Gauge charts showing performance vs. benchmark
- Heatmaps: Teams × Metrics colored by benchmark status (Over/Under/Within)
- Bar charts: Variance from benchmark by team and metric group

**Deliverable:** Benchmark analysis report with performance ratings

---

### Phase 3: Trend Visualization (REVISED)
**Objective:** Visualize metric trajectories across July-March period

**Key Considerations:**
- Focus on July-March period (April-June are 93-100% empty)
- Create separate visualizations per metric group
- Use team-level filtering for granular analysis
- Account for data sources with different measurement scales

**Visualizations:**
1. **Time-Series Line Charts**
   - Metric value vs. month
   - Separate line per team
   - Benchmark range highlighted as shaded background

2. **Multi-Metric Dashboards**
   - One dashboard per metric group (Quality, Reliability, Productivity, etc.)
   - 4-6 metrics per dashboard showing team trends

3. **Team Performance Cards**
   - Sparklines showing 8-month trend per metric
   - Status indicators: ↑ Improving, ↓ Declining, → Stable

4. **Comparative Heatmaps**
   - Teams (rows) × Months (columns) × Metric value (color)
   - One heatmap per metric group

5. **Moving Averages**
   - 3-month rolling average to smooth volatility
   - Overlay raw data with trend line

**Deliverable:** Suite of interactive and static visualizations

---

### Phase 4: Anomaly Detection (REVISED)
**Objective:** Flag unusual patterns, spikes, and deviations

**Techniques:**
1. **Statistical Outliers**
   - Z-score method (values > ±2 SD from team mean)
   - IQR method for robust detection

2. **Time-Series Anomalies**
   - Deviations from 3-month trend
   - Sudden rate-of-change spikes (month-over-month %)

3. **Comparative Anomalies**
   - Teams performing significantly different from peer group
   - Metrics diverging from historical baseline

4. **Seasonal/Cyclical Detection**
   - Identify if patterns repeat (unlikely with 8-month window, but check)

**Scoring:**
- Severity levels: Low (1.5-2 SD), Medium (2-3 SD), High (>3 SD)
- Confidence thresholds based on data completeness

**Deliverable:** Anomaly report with:
- Flagged data points ranked by severity
- Root cause investigation prompts
- Timeline of anomalies by team/metric

---

### Phase 5: Team & Metric Group Analysis
**Objective:** Deep-dive insights per team and metric category

**Analysis by Team (8 teams):**
- Overall health score (% metrics within/above benchmark)
- Strongest and weakest metric groups
- Trend direction summary (improving/declining/stable)
- Data completeness assessment

**Analysis by Metric Group (6 groups):**
- Cross-team performance comparison
- Benchmark compliance rate
- Most volatile metrics within group

**Deliverable:** 
- Team scorecards with key metrics
- Metric group benchmarking reports

---

### Phase 6: Integration & Automated Reporting
**Objective:** Extend MetricsAnalyzer and create reproducible reports

**Updates to src/analyzer.py:**
- `load_and_clean_data()` — Phase 0 implementation
- `validate_data_quality()` — Phase 1 checks
- `compare_benchmarks()` — Phase 2 analysis
- `visualize_trends()` — Phase 3 charts
- `detect_anomalies()` — Phase 4 detection
- `generate_team_scorecards()` — Phase 5 summaries
- `export_report()` — Generate HTML/PDF reports

**Code Structure:**
- Main analyzer improvements in `src/analyzer.py`
- Visualization functions in `src/visualization.py` (new)
- Cleaning utilities in `src/data_cleaning.py` (new)
- Anomaly detection in `src/anomaly_detection.py` (new)

**Testing:**
- Unit tests for each phase in `tests/test_analyzer.py`
- Data validation tests
- Visualization regression tests

**Deliverable:** 
- Enhanced MetricsAnalyzer class
- Automated report generation
- Test coverage > 80%

---

## Data-Specific Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Mixed data types in month columns | Parse with try/except, regex for patterns |
| 93% missing data in Apr-Jun | Focus analysis on Jul-Mar; flag period limitations |
| Percentage formats vary | Standardize to 0-100 numeric scale |
| Range benchmarks (80-85%) | Split into min/max, calculate compliance zone |
| 4 different data sources | Store source with metric, account for scale differences |
| Sparse metrics (many TBD sources) | Only analyze metrics with sufficient data points |

---

## Success Criteria
- [x] Data structure understood
- [ ] Phase 0: Data cleaning produces valid time-series
- [ ] Benchmark comparison complete for all teams
- [ ] 8+ visualizations created (Jul-Mar focus)
- [ ] Anomalies detected with >90% confidence scores
- [ ] Team scorecards generated
- [ ] MetricsAnalyzer extended with 6+ new methods
- [ ] Test coverage improved to >80%
- [ ] Automated report generation working
- [ ] Full analysis runnable with single command

---

## Technical Considerations

### Data Type Handling
```
Priority: fix month columns from object → numeric
Strategy: 
  - Try direct conversion
  - Parse special formats (%, "–", ranges)
  - Handle NaN/null appropriately
  - Document transformation for audit trail
```

### Analysis Period Limitation
- **Valid Period:** July through March (stable coverage)
- **Incomplete Period:** April-June (>93% null, exclude from trend analysis)
- **Note:** Report future analysis once full fiscal year data is collected

### Scaling Metrics
- Group metrics by unit type (%, count, days, hours, etc.)
- Create separate visualizations per unit type
- Or normalize within team/metric group (Z-score transformation)

---

## Deliverables Timeline

**Phase 0 (Foundation)** → Phase 1 (Quality Check) → Phase 2 (Benchmarking) → Phase 3 (Visualization) → Phase 4 (Anomalies) → Phase 5 (Deep-Dive) → Phase 6 (Integration)

Each phase produces documented output before proceeding to next phase.

---

## Next Immediate Steps
1. **Start Phase 0:** Create `src/data_cleaning.py` with transformation logic
2. **Implement:** `load_and_clean_data()` method in analyzer.py
3. **Validate:** Test data cleaning with sample metrics
4. **Document:** Create data transformation rules reference
