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

current_year_block = None

skip_words_upper = ["YEAR", "WEEK", "TOPIC", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", 
                    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "YEAR,WEEK,TOPIC",
                    "JANUARY 2026", "FEBRUARY 2026", "MARCH 2026", "APRIL 2026", "MAY 2026",
                    "DECEMBER 2025", "OCTOBER 2025", "SEPTEMBER 2025", "DECEMBER 2025", 
                    "JAN 2026", "FEB 2026", "MAR 2026", "APR 2026", "MAY 2026", "JAN 2025", "FEB 2025",
                    "DECEMBER 2025", "DECEMBER", "September", "October", "November", "December", "January", "February", "March", "April", "May"]
skip_words_upper = [w.upper() for w in skip_words_upper]

all_parsed = []

for row_idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    non_empty = [c for c in cells if c]
    if not non_empty:
        continue
        
    is_pure_header = True
    for val in non_empty:
        val_upper = val.upper()
        if "YEAR" in val_upper and any(ch.isdigit() for ch in val_upper):
            is_pure_header = False
            break
        if val_upper not in skip_words_upper:
            is_pure_header = False
            break
            
    if is_pure_header:
        continue
        
    # Find year block in this row to update current_year_block
    row_year_cell = None
    for cell in cells:
        if cell.upper().startswith("YEAR") and any(ch.isdigit() for ch in cell):
            row_year_cell = cell
            break
            
    if row_year_cell:
        current_year_block = row_year_cell
        
    if not current_year_block:
        continue
        
    for mapping in col_mapping:
        sc = mapping["start_col"]
        month = mapping["month"]
        
        if sc + 2 < len(cells):
            y_val = cells[sc]
            w_val = cells[sc + 1]
            t_val = cells[sc + 2]
            
            if w_val and t_val:
                t_upper = t_val.upper()
                w_upper = w_val.upper()
                skip_values = ["", "NA", "PENDING", "TOPIC", "YEAR", "WEEK"] + skip_words_upper
                if t_upper not in skip_values and w_upper not in skip_values:
                    year_level = y_val if (y_val.upper().startswith("YEAR") and any(ch.isdigit() for ch in y_val)) else current_year_block
                    all_parsed.append({
                        "row": row_idx + 1,
                        "year_block": current_year_block,
                        "year_level": year_level,
                        "month": month,
                        "week": w_val,
                        "topic": t_val
                    })

print(f"Total topics parsed: {len(all_parsed)}")
# Group by year block and subject name
grouped = {}
for p in all_parsed:
    yb = p["year_block"]
    if yb not in grouped:
        grouped[yb] = []
    grouped[yb].append(p)

for yb, items in grouped.items():
    print(f"\nYear Block: {yb} (Count: {len(items)})")
    # Print first 5 items
    for item in items[:5]:
        print(f"  Row {item['row']} | Month: {item['month']} | Week: {item['week']} | Topic: {item['topic']}")
    if len(items) > 5:
        print(f"  ... and {len(items) - 5} more")
