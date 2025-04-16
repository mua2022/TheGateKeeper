from datetime import datetime
from .database import attendance_collection

def log_attendance(student_id):
    today = datetime.now().date()
    last_log = attendance_collection.find_one(
        {"student_id": student_id, "date": str(today)},
        sort=[("_id", -1)]
    )

    if not last_log or "time_out" in last_log:
        time_in = datetime.now().strftime("%H:%M:%S")
        attendance_collection.insert_one({
            "student_id": student_id,
            "date": str(today),
            "time_in": time_in
        })
        return {"status": "Logged IN", "time": time_in}
    else:
        time_out = datetime.now().strftime("%H:%M:%S")
        attendance_collection.update_one(
            {"_id": last_log["_id"]},
            {"$set": {"time_out": time_out}}
        )
        return {"status": "Logged OUT", "time": time_out}
