import os
import django
import csv
import re
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem

def seed_syllabus():
    print("Beginning syllabus database ingestion...")
    
    # 1. Clear current items to avoid duplication
    print("Clearing existing resources and syllabus trackers...")
    SyllabusTracker.objects.all().delete()
    ResourceItem.objects.all().delete()
    
    csv_path = os.path.join("resources", "syllabus_tracker.csv")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_data = f.read().strip()
        
    lines = csv_data.split("\n")
    
    parsed_items = []
    
    # Define mapping columns & months from the CSV format
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
    
    rows = []
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        cells = list(csv.reader([line_str]))[0]
        rows.append(cells)
        
    for cells in rows:
        cells = [c.strip() for c in cells]
        non_empty = [c for c in cells if c]
        if not non_empty:
            continue
            
        # Is this row a pure header?
        # A pure header row is a row where all non-empty elements are header/metadata terms
        is_pure_header = True
        skip_words_upper = ["YEAR", "WEEK", "TOPIC", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", 
                            "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "YEAR,WEEK,TOPIC",
                            "JANUARY 2026", "FEBRUARY 2026", "MARCH 2026", "APRIL 2026", "MAY 2026",
                            "DECEMBER 2025", "OCTOBER 2025", "SEPTEMBER 2025", "DECEMBER 2025", 
                            "JAN 2026", "FEB 2026", "MAR 2026", "APR 2026", "MAY 2026", "JAN 2025", "FEB 2025",
                            "DECEMBER 2025", "DECEMBER", "September", "October", "November", "December", "January", "February", "March", "April", "May"]
        skip_words_upper = [w.upper() for w in skip_words_upper]
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
                    # Skip if the topic or week or month header is a placeholder
                    skip_values = ["", "NA", "PENDING", "TOPIC", "YEAR", "WEEK"] + skip_words_upper
                    if t_upper not in skip_values and w_upper not in skip_values:
                        year_level = y_val if (y_val.upper().startswith("YEAR") and any(ch.isdigit() for ch in y_val)) else current_year_block
                        parsed_items.append({
                            "year": year_level,
                            "month": month,
                            "week": w_val,
                            "topic": t_val
                        })
                        
    print(f"Parsed {len(parsed_items)} topics from spreadsheet CSV. Writing to database...")
    
    # Drive folder url mapping
    drive_base_url = "https://drive.google.com/drive/folders/1A448PqDCSgx0D09MjoBN7pmhs9vTS1eq"
    
    # 2. Seed Google Sheet Topics
    count = 0
    for item in parsed_items:
        # Determine subject name based on year level block
        y_name = item["year"]
        topic_name = item["topic"]
        week_str = item["week"]
        month_name = item["month"]
        
        # Match standard year name (strip foundation/higher/mock/further for folder cleanliness)
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
            
        # Parse numeric week number
        week_num = 1
        week_match = re.search(r'WK(\d+)', week_str, re.IGNORECASE)
        if week_match:
            week_num = int(week_match.group(1))
        else:
            # Fallback week num based on month
            month_weeks = {
                "SEPTEMBER": 1, "OCTOBER": 5, "NOVEMBER": 9, "DECEMBER": 13,
                "JANUARY": 17, "FEBRUARY": 21, "MARCH": 25, "APRIL": 29, "MAY": 33
            }
            week_num = month_weeks.get(month_name.upper(), 1)
            
        # Create syllabus tracker item
        tracker = SyllabusTracker.objects.create(
            board="Edexcel" if "12" in folder_year or "13" in folder_year else "GCSE",
            year_level=folder_year,
            subject=subject_name,
            topic=topic_name,
            subtopic=f"Study guide for {topic_name} - Scheduled in {month_name} ({week_str})",
            status="In Progress",
            covered_by="Stephen Jebadurai G"
        )
        
        # Create worksheet resources for all three formats (pdf, docx, pptx)
        safe_topic_slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_name)[:30].strip('_')
        for file_ext in ["pdf", "docx", "pptx"]:
            file_name = f"{folder_year.replace(' ', '')}_{subject_name.replace(' ', '')}_{safe_topic_slug}.{file_ext}"
            
            ResourceItem.objects.create(
                syllabus_match=tracker,
                year=folder_year,
                subject=subject_name,
                topic=topic_name,
                file_name=file_name,
                file_type=file_ext,
                drive_url=drive_base_url,
                week_number=week_num,
                month=month_name,
                week_string=week_str
            )
        count += 1
        
    print(f"Seeded {count} syllabus-matched resource worksheets successfully!")

    # 3. Seed Mock data for other primary years (Year 2, 3, 4, 5, 6) to ensure they are never empty
    print("Seeding Year 2, Year 3, Year 4, Year 5, and Year 6 folders with comprehensive national curriculum topics...")
    
    mock_years = ["Year 2", "Year 3", "Year 4", "Year 5", "Year 6"]
    mock_subjects = ["Maths", "English", "Science"]
    
    mock_topics = {
        "Maths": [
            "Fractions & Decimals", "Addition & Subtraction", "Multiplication Tables",
            "Division & Remainders", "Measurement & Time", "2D & 3D Geometry",
            "Graphs & Data Handling"
        ],
        "English": [
            "Spelling Patterns", "Punctuation Rules", "Noun & Verb Agreements",
            "Creative Writing Prompts", "Reading Comprehension", "Vocabulary Expansion"
        ],
        "Science": [
            "Plants & Ecosystems", "Animal Life Cycles", "Forces & Friction",
            "Light & Shadows", "Electricity Basics", "States of Matter"
        ]
    }
    
    mock_count = 0
    for y in mock_years:
        for subj in mock_subjects:
            topics = mock_topics[subj]
            for idx, topic_name in enumerate(topics):
                tracker = SyllabusTracker.objects.create(
                    board="GCSE Mapped",
                    year_level=y,
                    subject=subj,
                    topic=topic_name,
                    subtopic=f"National curriculum tracking for {topic_name}",
                    status="Completed" if idx % 2 == 0 else "In Progress",
                    covered_by="Stephen Jebadurai G"
                )
                
                safe_topic_slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_name).strip('_')
                months = ["SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY"]
                month_val = months[idx % len(months)]
                week_val = f"WK{(idx // 2) + 1}_DAY{(idx % 2) + 1}"
                
                for file_ext in ["pdf", "docx", "pptx"]:
                    file_name = f"{y.replace(' ', '')}_{subj}_{safe_topic_slug}.{file_ext}"
                    
                    ResourceItem.objects.create(
                        syllabus_match=tracker,
                        year=y,
                        subject=subj,
                        topic=topic_name,
                        file_name=file_name,
                        file_type=file_ext,
                        drive_url=drive_base_url,
                        week_number=idx + 1,
                        month=month_val,
                        week_string=week_val
                    )
                mock_count += 1
                
    print(f"Seeded {mock_count} mock curriculum-mapped items for primary school folders!")

    # 4. Seed other subjects for higher years (Year 7 to 13) to ensure complete directories
    print("Seeding other subjects (English, Biology, Chemistry, Physics) for higher years...")
    higher_years = ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11", "Year 12", "Year 13"]
    higher_subjects = ["English", "Biology", "Chemistry", "Physics"]
    
    higher_topics = {
        "English": [
            "Shakespearian Literature & Plays", "Poetry Analysis & Structure", 
            "Creative Writing & Narrative", "Persuasive Writing & Speech", 
            "Grammar, Punctuation & Rhetoric", "Reading Comprehension & Critical Analysis"
        ],
        "Biology": [
            "Cell Biology & Structure", "Photosynthesis & Plant Transport", 
            "Human Digestive System", "Cardiovascular & Respiratory Systems", 
            "Infectious Diseases & Immunology", "Genetics, DNA & Inheritance", 
            "Ecosystems & Biodiversity"
        ],
        "Chemistry": [
            "Atomic Structure & Periodic Table", "Chemical Bonding & Structure", 
            "Quantitative Chemistry & Moles", "Chemical Changes & Reactions", 
            "Energy Changes & Kinetics", "Organic Chemistry & Hydrocarbons"
        ],
        "Physics": [
            "Energy Stores & Conservation", "Electricity, Circuits & Charge", 
            "Particle Model of Matter", "Atomic Structure & Radioactivity", 
            "Forces, Motion & Newton's Laws", "Waves, Sound & Light"
        ]
    }
    
    higher_count = 0
    for y in higher_years:
        for subj in higher_subjects:
            topics = higher_topics[subj]
            for idx, topic_name in enumerate(topics):
                tracker = SyllabusTracker.objects.create(
                    board="Edexcel" if "12" in y or "13" in y else "GCSE",
                    year_level=y,
                    subject=subj,
                    topic=topic_name,
                    subtopic=f"Study guide and exercises for {topic_name}",
                    status="Completed" if idx % 2 == 0 else "In Progress",
                    covered_by="Stephen Jebadurai G"
                )
                
                safe_topic_slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_name).strip('_')
                months = ["SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY"]
                month_val = months[idx % len(months)]
                week_val = f"WK{(idx // 2) + 1}_DAY{(idx % 2) + 1}"
                
                for file_ext in ["pdf", "docx", "pptx"]:
                    file_name = f"{y.replace(' ', '')}_{subj}_{safe_topic_slug}.{file_ext}"
                    
                    ResourceItem.objects.create(
                        syllabus_match=tracker,
                        year=y,
                        subject=subj,
                        topic=topic_name,
                        file_name=file_name,
                        file_type=file_ext,
                        drive_url=drive_base_url,
                        week_number=idx + 1,
                        month=month_val,
                        week_string=week_val
                    )
                higher_count += 1
                
    print(f"Seeded {higher_count} mock curriculum-mapped higher years items for English, Biology, Chemistry, Physics!")
    print("Database syllabus ingestion fully complete and operational!")

if __name__ == '__main__':
    seed_syllabus()
