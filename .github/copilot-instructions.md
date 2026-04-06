# Copilot Instructions for TalentEngineeringMetricsAnalysis

Project for analyzing Talent Engineering Metrics.

## Project Overview

This Python project provides tools to analyze and visualize talent engineering metrics. The project is fully scaffolded with:
- Data analysis module (`src/analyzer.py`)
- Test suite (`tests/`)
- Required dependencies (pandas, numpy, matplotlib, seaborn, pytest)
- Documentation (README.md)

## Project Setup Checklist

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions (No extensions required)
- [x] Compile the Project
- [x] Create and Run Task
- [x] Launch the Project
- [x] Ensure Documentation is Complete

## Available Tasks

1. **Run Analyzer**: Executes the main analyzer module
2. **Run Tests**: Runs pytest to validate the project

## Getting Started

1. Activate the virtual environment (automatically created):
   ```bash
   .venv\Scripts\activate
   ```

2. Run the analyzer:
   - VS Code: Use the "Run Analyzer" task or press Ctrl+Shift+B
   - Terminal: `.venv\Scripts\python.exe src/analyzer.py`

3. Run tests:
   - VS Code: Select "Run Tests" from the task menu
   - Terminal: `.venv\Scripts\python.exe -m pytest tests/`

## Project Structure

```
src/
  ├── __init__.py
  └── analyzer.py          # Main MetricsAnalyzer class

tests/
  ├── __init__.py
  └── test_analyzer.py     # Unit tests

requirements.txt           # Python dependencies
setup.py                   # Package configuration
README.md                  # Project documentation
.gitignore                 # Git ignore patterns
```

## Next Steps

- Load data using `MetricsAnalyzer('path/to/data.csv')`
- Extend analyzer with new metrics and visualizations
- Add more comprehensive tests as features grow
