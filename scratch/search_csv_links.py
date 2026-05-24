import os

csv_path = os.path.join("resources", "syllabus_tracker.csv")
with open(csv_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Contains drive.google.com:", "drive.google.com" in content)
print("Contains http:", "http" in content)
print("Contains folders:", "folders" in content)
