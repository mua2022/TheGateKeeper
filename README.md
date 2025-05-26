# TheGateKeeper
# User Manual: AI-Based Student Recognition and Logging System
## 1. Introduction
Welcome to the AI University Student Logging System — a smart attendance and access control solution that uses face recognition technology to automatically log students in or out of a university campus. This manual provides guidance on how to use the system's features efficiently, including registration, logging, memo management, and report generation.

## 2. System Requirements
*Hardware*

Webcam (built-in or USB)

Computer with minimum 4GB RAM

At least 10GB of free disk space

*Software*

Python 3.10 or higher

Required libraries: face_recognition, opencv-python, tkinter, reportlab, sqlite3, smtplib, fitz, etc.

## 3. Launching the System
Step 1: Open a terminal or command prompt.
Step 2: Navigate to the project directory.

``cd TheGateKeeper``

Step 3: Run the application

``python main.py``

The system GUI will open automatically.

## 4. Main Features and How to Use Them
### 4.1 Registering a Student
Click *“Register Student”*.

Fill in:

Student ID

Full Name

Email Address

Course (select from the dropdown)

Choose one of the two options:

📷 Capture via Camera – Capture 4 face images in real-time.

📁 Upload Images – Upload existing student face images.

The system will encode the images and store them in the local database.

After registration, the system automatically retrains encodings.

### 4.2 Start Face Recognition & Logging
Click *“Start Camera”*.

When a registered student appears in front of the webcam:

The system will detect their face.

Automatically logs them in or out depending on their last status.

Displays their name, ID, and current status.

Sends a personalized email with their class schedule for the day (if available).

### 4.3 Train Dataset
Use this if you manually added student images or updated face data.

Click *“Train Dataset”*

The system processes all student image folders.

Encodings are saved to the model file.

### 4.4 View Registered Students
Click *“View Students”*

See a list of:

Student IDs

Full Names

Email addresses

Course

Select a student and click “Delete Selected” to remove them.

### 4.5 Filter Attendance Logs by Date
Click *“Report Genarator”*

Enter the date in the format YYYY-MM-DD

View logs for all students on that specific date

### 4.6 Upload Memos
Click *“Upload Memo”*

Select a PDF file (memo)

The file is stored and emailed to all students in the database.

### 4.7 Upload Timetable
Click *“Upload Timetable”*

Select the PDF file of the timetable

The system automatically parses the document and maps units to courses and days.

### 4.8 Generate Reports
Click *“Generate Report”*

Choose filter:

By Student ID

By Date

The system generates a PDF report of attendance and stores it in the reports/ directory.

### 5. Email Integration
Emails are sent using Gmail. You must:

Enable 2-Step Verification on your Gmail account.

Create a Gmail App Password.

Replace credentials in display.py or .env file:

``GMAIL_ADDRESS = "your_email@gmail.com"``

``GMAIL_APP_PASSWORD = "your_generated_app_password"``
## 6. Folder Structure

TheGateKeeper/

├── gui/

│   └── display.py

├── database/

│   └── attendance.db

├── face_recognizer/

│   └── trainer.py

├── utils/

│   └── time_utils.py

│   └── notification.py

├── student_images/

├── reports/

├── memos/

├── timetable_parser.py

├── main.py
## 7. Troubleshooting
*Issue	Possible Cause	Solution*
Camera not opening	Camera already in use or blocked	Close other apps or restart your computer
Face not recognized	Poor lighting, image not trained	Ensure good lighting, retrain dataset
Email not sent	Incorrect app password or email config	Check Gmail app password and internet access
Timetable parse error	Wrong format or inconsistent labels	Use well-structured timetable PDFs
GUI Freeze/Crash	Overloaded main thread	Let system complete processing before retry

## 8. Maintenance & Backup
Regularly backup the attendance.db file.

Keep a backup of the student_images/ and encodings.pkl.

Clear outdated logs from the database monthly if needed.

## 9. Contact & Support
If you encounter bugs, performance issues, or need help:

Email developer: [muaemmanuel2022@gmail.com]

GitHub/Support Repo: [https://github.com/mua2022]
