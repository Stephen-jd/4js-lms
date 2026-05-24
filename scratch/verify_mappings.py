import os
import csv
import django
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem

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

csv_parsed = []
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
        
    # Update current year block
    for cell in cells:
        if cell.upper().startswith("YEAR") and any(ch.isdigit() for ch in cell):
            current_year_block = cell
            break
            
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
                    csv_parsed.append({
                        "row": row_idx + 1,
                        "year": year_level,
                        "month": month,
                        "week": w_val,
                        "topic": t_val
                    })

print(f"Total parsed from CSV: {len(csv_parsed)}")

# Compare each parsed CSV item with what is in SQLite
failures = 0
for idx, item in enumerate(csv_parsed):
    t_name = item["topic"]
    w_str = item["week"]
    m_name = item["month"]
    y_name = item["year"]
    
    # Query database for a ResourceItem matching this
    # We need to map y_name to folder_year and subject_name like in seed_syllabus.py
    folder_year = "Year 7"
    subject_name = "Maths"
    y_name_lower = y_name.lower()
    if "year 7" in y_name_lower:
        folder_year = "Year 7"
        subject_name = "Maths"
    elif "year 8" in y_name_lower:
        folder_year = "Year 8"
        subject_name = "Maths"
    elif "year 9" in y_name_lower:
        folder_year = "Year 9"
        subject_name = "Maths"
    elif "year 10 mock" in y_name_lower:
        folder_year = "Year 10"
        subject_name = "Maths Mocks"
    elif "year 10" in y_name_lower:
        folder_year = "Year 10"
        subject_name = "Maths"
    elif "year 11 mock" in y_name_lower:
        folder_year = "Year 11"
        subject_name = "Maths Mocks"
    elif "year 11 foundation" in y_name_lower:
        folder_year = "Year 11"
        subject_name = "Maths (Foundation)"
    elif "year 11 higher" in y_name_lower:
        folder_year = "Year 11"
        subject_name = "Maths (Higher)"
    elif "year 11" in y_name_lower:
        folder_year = "Year 11"
        subject_name = "Maths"
    elif "year 12- further" in y_name_lower or "further maths" in y_name_lower:
        folder_year = "Year 12"
        subject_name = "Further Maths"
    elif "mechanic" in y_name_lower:
        folder_year = "Year 12"
        subject_name = "Mechanics Maths"
    elif "year 12" in y_name_lower:
        folder_year = "Year 12"
        subject_name = "Maths (Pure)"
    elif "year 13" in y_name_lower:
        folder_year = "Year 13"
        subject_name = "Maths (A-Level)"
    else:
        folder_year = y_name
        subject_name = "Maths"
        
    db_items = ResourceItem.objects.filter(year=folder_year, subject=subject_name, topic=t_name, month=m_name, week_string=w_str)
    if not db_items.exists():
        failures += 1
        print(f"Mismatch at CSV Row {item['row']}:")
        print(f"  CSV: Year='{y_name}', Subject='{subject_name}', Topic='{t_name}', Month='{m_name}', Week='{w_str}'")
        # Let's see what is in the DB for this topic
        partial_match = ResourceItem.objects.filter(topic=t_name).first()
        if partial_match:
            print(f"  DB partial: Year='{partial_match.year}', Subject='{partial_match.subject}', Topic='{partial_match.topic}', Month='{partial_match.month}', Week='{partial_match.week_string}'")
        else:
            print("  DB: No entry at all with this topic name")

print(f"Total verification mismatches: {failures}")
