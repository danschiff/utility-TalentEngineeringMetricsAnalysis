import pandas as pd
import yaml

from src.team_level_template_extractor import (
    build_team_month_metric_dict,
    get_month_columns,
    load_team_level_template,
    write_yaml,
)


def test_get_month_columns_returns_expected_headers():
    df = pd.DataFrame({
        'Team': [],
        'Metric': [],
        'July': [],
        'August': [],
        'Extra': [],
    })

    months = get_month_columns(df)

    assert months == ['July', 'August']


def test_build_team_month_metric_dict_produces_nested_structure():
    df = pd.DataFrame([
        {
            'Team': 'Alpha',
            'Metric Group': 'Quality',
            'Source': 'System',
            'Metric': 'Bug Rate',
            'Industry Benchmarks': '0-2%',
            'July': 1.5,
            'August': 2.1,
        },
        {
            'Team': 'Beta',
            'Metric Group': 'Velocity',
            'Source': 'Jira',
            'Metric': 'Story Points',
            'Industry Benchmarks': 'TBD',
            'July': 120,
            'August': None,
        },
    ])
    months = ['July', 'August']
    nested = build_team_month_metric_dict(df, months)

    assert nested['Alpha']['July'][0]['metric'] == 'Bug Rate'
    assert nested['Alpha']['July'][0]['value'] == 1.5
    assert nested['Alpha']['August'][0]['value'] == 2.1
    assert nested['Beta']['August'][0]['value'] is None
    assert nested['Beta']['July'][0]['source'] == 'Jira'


def test_write_yaml_writes_file(tmp_path):
    data = {
        'Alpha': {
            'July': [
                {'metric': 'Bug Rate', 'value': 1.5},
            ],
        },
    }
    output_file = tmp_path / 'output.yml'
    result_path = write_yaml(data, output_file)

    assert result_path.exists()
    loaded = yaml.safe_load(output_file.read_text(encoding='utf-8'))
    assert loaded == data


def test_load_team_level_template_reads_excel_file(tmp_path):
    excel_path = tmp_path / 'sample.xlsx'
    sheet_name = 'Team-Level Template'
    df = pd.DataFrame(
        [
            {
                'Team': 'Alpha',
                'Metric Group': 'Quality',
                'Source': 'System',
                'Metric': 'Bug Rate',
                'Industry Benchmarks': '0-2%',
                'July': 1.5,
            }
        ]
    )
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    loaded_df = load_team_level_template(excel_path)
    assert list(loaded_df.columns) == list(df.columns)
    assert loaded_df.loc[0, 'Team'] == 'Alpha'
