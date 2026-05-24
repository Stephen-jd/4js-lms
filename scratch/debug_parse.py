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

# Row 89 corresponds to index 88 (since rows was 0-indexed in our debug_parse, but let's find the one containing "Modeling mechanics")
for idx, r in enumerate(rows):
    r_str = ",".join(r)
    if "Modeling mechanics" in r_str:
        print(f"Row {idx+1} length: {len(r)}")
        for col_idx, val in enumerate(r):
            print(f"  Col {col_idx}: '{val}'")
