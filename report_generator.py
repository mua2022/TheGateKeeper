import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

DB_PATH = 'database/attendance.db'
REPORT_DIR = 'reports'

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

class ReportGenerator:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Generate Attendance Report")

        # Filter options
        filter_frame = tk.LabelFrame(self.top, text="Filter Logs")
        filter_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(filter_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
        self.student_entry = tk.Entry(filter_frame)
        self.student_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Date:").grid(row=0, column=2, padx=5, pady=5)
        self.date_entry = DateEntry(filter_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(filter_frame, text="Fetch Logs", command=self.fetch_logs).grid(row=0, column=4, padx=10)
        tk.Button(filter_frame, text="Export to PDF", command=self.export_to_pdf).grid(row=0, column=5, padx=10)

        # Table to show logs
        self.tree = ttk.Treeview(self.top, columns=("Student ID", "Name", "Time", "Status"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.current_data = []

    def fetch_logs(self):
        student_id = self.student_entry.get().strip()
        date_val = self.date_entry.get_date().strftime('%Y-%m-%d')

        query = "SELECT student_id, name, timestamp, status FROM attendance WHERE 1=1"
        params = []

        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)

        if date_val:
            query += " AND DATE(timestamp) = ?"
            params.append(date_val)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        self.current_data = rows

        if rows:
            for row in rows:
                self.tree.insert('', tk.END, values=row)
        else:
            messagebox.showinfo("No Records", "No logs found for the specified filters.")

    def export_to_pdf(self):
        if not self.current_data:
            messagebox.showerror("No Data", "Please fetch logs before exporting.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(REPORT_DIR, f"attendance_report_{timestamp}.pdf")

        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, "Attendance Report ")

        c.setFont("Helvetica", 11)
        y = height - 80
        c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 30

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Student ID")
        c.drawString(150, y, "Name")
        c.drawString(300, y, "Timestamp")
        c.drawString(450, y, "Status")
        y -= 20
        c.setFont("Helvetica", 10)

        for row in self.current_data:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, str(row[0]))
            c.drawString(150, y, str(row[1]))
            c.drawString(300, y, str(row[2]))
            c.drawString(450, y, str(row[3]))
            y -= 15

        c.save()
        messagebox.showinfo("Export Complete", f"PDF saved to: {filename}")
