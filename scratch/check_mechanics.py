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

# Print rows that contain "mechanic" (case insensitive)
for row_idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    cells_str = ",".join(cells)
    if "mechanic" in cells_str.lower():
        print(f"\n--- Row {row_idx} (1-based line: {row_idx + 1}) ---")
        print(f"Num cells: {len(cells)}")
        for idx, cell in enumerate(cells):
            if cell:
                print(f"  Col {idx}: {cell}")
        
        # Let's see what is parsed from this row using the seeder logic:
        current_year_block = None
        for cell in cells:
            if cell.upper().startswith("YEAR") and any(ch.isdigit() for ch in cell):
                current_year_block = cell
                break
        print(f"  Detected current_year_block from row: {current_year_block}")
        
        # Parse items:
        for mapping in col_mapping:
            sc = mapping["start_col"]
            month = mapping["month"]
            if sc + 2 < len(cells):
                y_val = cells[sc]
                w_val = cells[sc + 1]
                t_val = cells[sc + 2]
                if w_val or t_val:
                    print(f"    Mapping {month} (sc={sc}): Y='{y_val}', W='{w_val}', T='{t_val}'")
