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

# Let's find rows containing "Mechanic" or "Year 12"
for idx, cells in enumerate(rows):
    cells = [c.strip() for c in cells]
    non_empty = [c for c in cells if c]
    if any("MECHANIC" in c.upper() for c in non_empty):
        print(f"Row {idx}: {cells[:15]}... len: {len(cells)}")
        print(f"Non-empty values in row {idx}: {non_empty}")
