import pandas as pd

excel_file = r"c:\Code\Paylocity\utility-TalentEngineeringMetricsAnalysis\input\Talent Engineering Metrics.xlsx"

xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

print("Sheet names:", sheet_names)
print("\n" + "="*80 + "\n")

for sheet in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    print(f"SHEET: {sheet}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nData types:\n{df.dtypes}")
    print("\n" + "="*80 + "\n")