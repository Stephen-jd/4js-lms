import os
import csv
import re

csv_path = os.path.join("resources", "syllabus_tracker.csv")
with open(csv_path, 'r', encoding='utf-8') as f:
    csv_data = f.read().strip()
    
lines = csv_data.split("\n")
rows = []
for line in lines:
    line_str = line.strip()
    if not line_str:
        continue
    cells = list(csv.reader([line_str]))[0]
    rows.append(cells)

col_mapping = [
    {"start_col": 0, "month": "SEPTEMBER"},
    {"start_col": 4, "month": "OCTOBER"},
    {"start_col": 8, "month": "NOVEMBER"},
    {"start_col": 11, "month": "DECEMBER"},
    {"start_col": 14, "month": "JANUARY"},
    {"start_col": 17, "month": "FEBRUARY"},
    {"start_col": 20, "month": "MARCH"},
    {"start_col": 23, "month": "APRIL"},
    {"start_col": 26, "month": "MAY"},
]

unique_year_vals = set()

for row_idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    for mapping in col_mapping:
        sc = mapping["start_col"]
        if sc < len(cells):
            y_val = cells[sc]
            if y_val:
                unique_year_vals.add(y_val)

print("Unique non-empty year column values in CSV:")
for val in sorted(unique_year_vals):
    starts_with_year = val.upper().startswith("YEAR")
    has_digit = any(ch.isdigit() for ch in val)
    print(f"  '{val}' -> starts_with_year: {starts_with_year}, has_digit: {has_digit}")
