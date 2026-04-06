# TalentEngineeringMetricsAnalysis

A Python project for analyzing Talent Engineering Metrics.

## Project Overview

This project provides tools to analyze and visualize talent engineering metrics, helping to generate insights from talent data.

## Project Structure

```
TalentEngineeringMetricsAnalysis/
├── src/
│   ├── __init__.py
│   └── analyzer.py          # Main analyzer module
├── tests/
│   ├── __init__.py
│   └── test_analyzer.py     # Unit tests
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore             # Git ignore patterns
└── .github/
    └── copilot-instructions.md  # Copilot setup instructions
```

## Installation

1. Ensure Python 3.7+ is installed.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Analyzer

```python
from src.analyzer import MetricsAnalyzer

# Initialize analyzer
analyzer = MetricsAnalyzer('path/to/data.csv')

# Get summary statistics
summary = analyzer.get_summary()
print(summary)

# Analyze metrics
results = analyzer.analyze_metrics()
print(results)
```

### Extracting Team-Level Metrics to YAML

```bash
python -m src.team_level_template_extractor \
  input/Talent Engineering Metrics.xlsx \
  output/team_metrics.yaml
```

This will read the `Team-Level Template` sheet and write a nested YAML structure organized by team and month.

### Running Tests

```bash
pytest tests/
```

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Data visualization
- **seaborn**: Statistical data visualization
- **pytest**: Testing framework

## Contributing

Please ensure all code follows PEP 8 style guidelines and includes appropriate tests.

## License

[Add your license information here]

## Contact

For questions or issues, please contact the development team.
