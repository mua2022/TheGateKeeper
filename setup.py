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

#{
#   "monday": {
#     "bsey1s2": [
#       {
#         "lecturer": "Mr. kibe",
#         "unit_code": "CSE2126 SAD",
#         "time": "8.00-10.00 AM"
#       }
#     ],
#     "bsey2s2": [
#       {
#         "lecturer": "Dr. Liech",
#         "unit_code": "CSE2231 DB2",
#         "time": "8.00-11.00 AM"
#       }
#     ],
#     "bsey3s2": [
#       {
#         "lecturer": "Njiru Nick",
#         "unit_code": "CSE2321 DSA",
#         "time": "11.00-1.00 PM"
#       }
#     ],
#     "bsey4s2": [
#       {
#         "lecturer": "Prof. Odeo",
#         "unit_code": "CSE2421 CSEC",
#         "time": "2.00-5.00 PM"
#       }
#     ],
#     "bity1s2": [
#       {
#         "lecturer": "Charles Njigi",
#         "unit_code": "CCS2122 SE",
#         "time": "8.00-10.00 AM"
#       }
#     ],
#     "bity2s2": [
#       {
#         "lecturer": "Geofrey Manoti",
#         "unit_code": "CCS2222 ODE",
#         "time": "11.00-1.00 PM"
#       }
#     ],
#     "bity3s2": [
#       {
#         "lecturer": "Alex Smith",
#         "unit_code": "CCS2321 DS",
#         "time": "11.00-1.00 PM"
#       }
#     ],
#     "bity4s2": [
#       {
#         "lecturer": "Dr. Karanja Karis",
#         "unit_code": "CCS2421 EC",
#         "time": "8.00-10.00 AM"
#       }
#     ],
#     "bcty1s2": [
#       {
#         "lecturer": "Eliza Shadrack",
#         "unit_code": "BCT2123 BN",
#         "time": "2.00-5.00 PM"
#       }
#     ],
#     "bcty2s2": [
#       {
#         "lecturer": "Smith Kinyash",
#         "unit_code": "BCT2221 SN",
#         "time": "8.00-10.00 AM"
#       }
#     ],
#     "bcty3s2": [
#       {
#         "lecturer": "Nderitu Kinuthia",
#         "unit_code": "BCT2324 CS",
#         "time": "11.00-1.00 PM"
#       }
#     ],
#     "bcty4s2": [
#       {
#         "lecturer": "Dr. Muturi",
#         "unit_code": "BCT2425 CT",
#         "time": "2.00-5.00 PM"
#       }
#     ]
#   }
# }
