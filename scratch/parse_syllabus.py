import csv

def parse_syllabus():
    csv_path = r"C:\Users\steph\.gemini\antigravity\brain\ae316e04-d22e-446c-8dcb-62dc253bad71\.system_generated\steps\578\content.md"
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    parts = content.split("---")
    csv_data = parts[-1].strip()
    
    lines = csv_data.split("\n")
    
    parsed_items = []
    
    # Pre-defined columns matching the CSV alignment
    col_mapping = [
        {"start_col": 0, "default_month": "SEPTEMBER"},
        {"start_col": 4, "default_month": "OCTOBER"},
        {"start_col": 8, "default_month": "NOVEMBER"},
        {"start_col": 11, "default_month": "DECEMBER"},
        {"start_col": 14, "default_month": "JANUARY"},
        {"start_col": 17, "default_month": "FEBRUARY"},
        {"start_col": 20, "default_month": "MARCH"},
        {"start_col": 23, "default_month": "APRIL"},
        {"start_col": 26, "default_month": "MAY"},
    ]
    
    current_year_block = None
    
    # We will first parse all lines into list of cell lists
    rows = []
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        cells = list(csv.reader([line_str]))[0]
        rows.append(cells)
        
    # Now let's iterate rows
    for r_idx, cells in enumerate(rows):
        # Skip header rows
        if any(h in "".join(cells).upper() for h in ["SEPTEMBER", "YEAR,WEEK,TOPIC"]):
            continue
            
        # Check if first cell has a year block definition
        # (e.g. starts with "Year ")
        first_cell = cells[0].strip() if len(cells) > 0 else ""
        if first_cell.upper().startswith("YEAR"):
            current_year_block = first_cell
            
        if not current_year_block:
            continue
            
        # Parse topics for each mapped column group in this row
        for mapping in col_mapping:
            sc = mapping["start_col"]
            month = mapping["default_month"]
            
            if sc + 2 < len(cells):
                y_val = cells[sc].strip()
                w_val = cells[sc + 1].strip()
                t_val = cells[sc + 2].strip()
                
                # Clean and check
                if w_val and t_val:
                    t_upper = t_val.upper()
                    if t_upper not in ["", "NA", "PENDING", "TOPIC"]:
                        # Extract the year level:
                        # use y_val if it has "Year", otherwise use current_year_block
                        year_level = y_val if y_val.upper().startswith("YEAR") else current_year_block
                        
                        parsed_items.append({
                            "year": year_level,
                            "month": month,
                            "week": w_val,
                            "topic": t_val
                        })
                        
    print(f"Successfully parsed {len(parsed_items)} topics!")
    # Print a few to inspect
    for item in parsed_items[:30]:
        print(item)

if __name__ == '__main__':
    parse_syllabus()
