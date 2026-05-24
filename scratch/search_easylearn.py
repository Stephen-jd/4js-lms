import os

root_dir = "c:\\Users\\steph\\Downloads\\4j-lms"
found = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    if "venv" in dirpath or ".git" in dirpath or "__pycache__" in dirpath or ".system_generated" in dirpath:
        continue
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".html", ".js", ".css", ".py", ".ts", ".txt", ".json"]:
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "easylearn" in content.lower() or "easy learn" in content.lower():
                    found.append(file_path)
            except Exception as e:
                pass

print("Files containing 'easylearn' or 'easy learn':")
for f in found:
    print(f"  {f}")
