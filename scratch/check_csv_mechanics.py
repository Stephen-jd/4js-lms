import csv

csv_path = "resources/syllabus_tracker.csv"
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

print("Scanning CSV for Mechanics topics...")
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

mechanics_csv_items = []
current_year_block = None

for r_idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    first_cell = cells[0] if len(cells) > 0 else ""
    if first_cell.upper().startswith("YEAR") and any(ch.isdigit() for ch in first_cell):
        current_year_block = first_cell
        
    for mapping in col_mapping:
        sc = mapping["start_col"]
        month = mapping["month"]
        if sc + 2 < len(cells):
            y_val = cells[sc]
            w_val = cells[sc + 1]
            t_val = cells[sc + 2]
            
            # If the topic is non-empty and not in skip words
            if t_val and w_val:
                t_upper = t_val.upper()
                if t_upper not in ["", "NA", "PENDING", "TOPIC", "YEAR", "WEEK"]:
                    year_level = y_val if (y_val.upper().startswith("YEAR") and any(ch.isdigit() for ch in y_val)) else current_year_block
                    
                    # Check if this belongs to mechanics
                    is_mech = False
                    if year_level and "mechanic" in year_level.lower():
                        is_mech = True
                    elif y_val and "mechanic" in y_val.lower():
                        is_mech = True
                        
                    if is_mech:
                        mechanics_csv_items.append({
                            "row": r_idx + 1,
                            "year_resolved": year_level,
                            "y_val": y_val,
                            "month": month,
                            "week": w_val,
                            "topic": t_val
                        })

print(f"Total Mechanics topics found in CSV: {len(mechanics_csv_items)}")
for item in mechanics_csv_items:
    print(f"Row {item['row']}: {item['month']} ({item['week']}) - YearResolved='{item['year_resolved']}' - y_val='{item['y_val']}' - Topic='{item['topic']}'")
