import csv
import re

with open("resources/syllabus_tracker.csv", 'r', encoding='utf-8') as f:
    lines = f.read().strip().split("\n")

years_found = set()
for line in lines:
    line_str = line.strip()
    if not line_str:
        continue
    cells = list(csv.reader([line_str]))[0]
    for cell in cells:
        match = re.search(r'\b(Year\s+\d+)\b', cell, re.IGNORECASE)
        if match:
            years_found.add(match.group(1).title())

print("Years found in CSV file:")
print(sorted(list(years_found)))
