import os

csv_path = os.path.join("resources", "syllabus_tracker.csv")
with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(79, 105):
    if idx < len(lines):
        print(f"Line {idx+1}: {lines[idx].strip()}")
