import os

js_path = os.path.join("static", "js", "main.js")
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "state.db" in line or "fetch" in line or "resources" in line:
        if any(term in line for term in ["state.db = ", "const db", "window.db", "/api/resources"]):
            print(f"Line {idx+1}: {line.strip()}")
