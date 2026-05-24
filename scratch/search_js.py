import os

js_path = os.path.join("static", "js", "main.js")
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

search_terms = ["filter-year", "filter-subject", "renderResources", "renderSyllabus", "renderFolder", "renderYear", "subject", "topic"]

for idx, line in enumerate(lines):
    line_str = line.strip()
    for term in search_terms:
        if term in line_str:
            print(f"Line {idx+1}: {line_str[:120]}")
            break
