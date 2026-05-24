import os
import csv

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

# Let's inspect row 3 (which is index 2, the headers row)
header_row = rows[2]
print("Header row length:", len(header_row))
for idx, val in enumerate(header_row):
    print(f"Col {idx}: {val}")

# Let's print row 4 (index 3) to see the values at the indices
first_data_row = rows[3]
print("\nFirst data row length:", len(first_data_row))
for idx, val in enumerate(first_data_row):
    print(f"Col {idx}: {val}")
