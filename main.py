from gui.display import FaceRecognitionApp
from database.db_handler import init_db
import tkinter as tk

init_db()

if __name__ == '__main__':
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
