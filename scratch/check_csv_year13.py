import csv

with open("resources/syllabus_tracker.csv", 'r', encoding='utf-8') as f:
    lines = f.read().strip().split("\n")

rows = []
for line in lines:
    line_str = line.strip()
    if not line_str:
        continue
    cells = list(csv.reader([line_str]))[0]
    rows.append(cells)

print("=== Year 13 CSV Rows ===")
for idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    non_empty = [c for c in cells if c]
    if any("YEAR 13" in c.upper() for c in non_empty):
        print(f"Row {idx:02d}: non-empty elements -> {non_empty}")
