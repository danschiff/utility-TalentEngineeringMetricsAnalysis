## Plan: Extract Team Monthly Metrics to YAML

TL;DR: Add a focused extractor module that reads the "Team-Level Template" sheet from `input/Talent Engineering Metrics.xlsx`, builds a nested YAML structure by team and month, and writes it to an output YAML file. Keep the scope limited to data extraction only; no PowerPoint generation.

**Steps**
1. Add a new module `src/team_level_template_extractor.py`.
   - Implement `load_team_level_template(data_path)` to read the Excel workbook and the `Team-Level Template` sheet.
   - Implement `get_month_columns(df)` to detect or validate the month columns from the sheet header.
   - Implement `build_team_month_metric_dict(df, month_columns)` to create a nested dict of teams containing months containing metric values.
   - Implement `write_yaml(data, output_path)` using `yaml.safe_dump`.
2. Add YAML dependency support.
   - Install and add `PyYAML` to `requirements.txt`.
   - Add `PyYAML` to `install_requires` in `setup.py`.
3. Add tests in `tests/test_team_level_template_extractor.py`.
   - Cover reading a sample DataFrame, building the nested team/month/metric structure, and serializing YAML output.
4. Update `README.md` with a short usage example for the new extractor script.

**Verification**
1. Run the new extractor against `input/Talent Engineering Metrics.xlsx` and verify that output YAML contains the expected nested structure for teams and months.
2. Run `pytest tests/test_team_level_template_extractor.py` and confirm passing tests.
3. Confirm the output YAML is valid and openable by a YAML parser.

**Decisions**
- The output YAML will be nested by team, then month, then metrics.
- The scope is limited to extracting and serializing the data, not PowerPoint deck population.
- Month column detection should be robust to the existing template columns, but the actual month headers should be verified from the workbook.

**Further Considerations**
1. If the workbook column names differ from the expected month names, add a normalization step or configurable mapping.
2. If metrics should include additional metadata (e.g. source, metric group), that can be added later without changing the core extraction pattern.
