"""Extractor for the Team-Level Template worksheet."""

import argparse
from datetime import datetime, date, time
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_MONTHS = [
    'July', 'August', 'September', 'October', 'November', 'December',
    'January', 'February', 'March', 'April', 'May', 'June',
]


def load_team_level_template(data_path, sheet_name='Team-Level Template'):
    """Load the Team-Level Template sheet from an Excel workbook."""
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Input file not found: {data_path}")

    if data_path.suffix.lower() not in {'.xlsx', '.xls'}:
        raise ValueError('Only Excel files are supported for Team-Level Template extraction.')

    return pd.read_excel(data_path, sheet_name=sheet_name)


def get_month_columns(df, expected_months=None):
    """Return the month columns present in the template, preserving sheet order."""
    expected_months = expected_months or DEFAULT_MONTHS
    month_columns = [col for col in df.columns if isinstance(col, str) and col.strip() in expected_months]

    if not month_columns:
        raise ValueError('No month columns were detected in the Team-Level Template sheet.')

    return month_columns


def normalize_value_for_yaml(value):
    """Normalize values so they can be safely serialized to YAML."""
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def build_team_month_metric_dict(df, month_columns):
    """Build a nested structure organized by team, month, and metric."""
    output = {}

    for _, row in df.iterrows():
        team_name = str(row.get('Team', '')).strip() or 'Unknown'
        metric_name = str(row.get('Metric', '')).strip()
        if not metric_name:
            continue

        metric_group = row.get('Metric Group')
        source = row.get('Source')
        benchmark = row.get('Industry Benchmarks')

        for month in month_columns:
            raw_value = row.get(month)
            value = None if pd.isna(raw_value) else normalize_value_for_yaml(raw_value)

            team_data = output.setdefault(team_name, {})
            month_data = team_data.setdefault(month, [])

            entry = {
                'metric': metric_name,
                'value': value,
            }
            if pd.notna(metric_group):
                entry['metric_group'] = str(metric_group).strip()
            if pd.notna(source):
                entry['source'] = str(source).strip()
            if pd.notna(benchmark):
                entry['industry_benchmarks'] = str(benchmark).strip()

            month_data.append(entry)

    return output


def write_yaml(data, output_path):
    """Write the extracted structure to a YAML file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w', encoding='utf-8') as output_file:
        yaml.safe_dump(data, output_file, sort_keys=False, allow_unicode=True)

    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract monthly team metrics from the Team-Level Template sheet into YAML.'
    )
    parser.add_argument('input_excel', help='Path to the input Excel workbook.')
    parser.add_argument('output_yaml', help='Path to write the output YAML file.')
    return parser.parse_args()


def main():
    args = parse_args()
    df = load_team_level_template(args.input_excel)
    month_columns = get_month_columns(df)
    extracted = build_team_month_metric_dict(df, month_columns)
    output_path = write_yaml(extracted, args.output_yaml)
    print(f'Wrote extracted YAML to: {output_path}')


if __name__ == '__main__':
    main()
