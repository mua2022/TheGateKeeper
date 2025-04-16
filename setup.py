import os

folders = [
    "database",
    "face_recognition",
    "gui",
    "student_images",
    "utils",
    "output",
    "assets"
]

files = {
    "main.py": "",
    "requirements.txt": "",
    "database/db_handler.py": "",
    "face_recognition/encoder.py": "",
    "face_recognition/recognizer.py": "",
    "gui/display.py": "",
    "utils/time_utils.py": "",
    "output/attendance_log.csv": "",
    "assets/logo.png": ""
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for filepath, content in files.items():
    with open(filepath, 'w') as f:
        f.write(content)

print("✅ Project structure created successfully!")
