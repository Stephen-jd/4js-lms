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

for idx in range(74, 100):
    if idx < len(rows):
        cells = [c.strip() for c in rows[idx]]
        print(f"Row {idx:02d}: {cells}")
