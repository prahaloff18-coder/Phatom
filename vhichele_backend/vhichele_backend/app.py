from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

# ---------------- DATABASE ----------------
conn = sqlite3.connect("vehicles.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    type TEXT,
    frame INTEGER,
    x1 INTEGER,
    y1 INTEGER,
    x2 INTEGER,
    y2 INTEGER
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    alert_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ---------------- DATA MODEL ----------------
class Vehicle(BaseModel):
    vehicle_id: int
    type: str
    frame: int
    bbox: List[int]

class Alert(BaseModel):
    vehicle_id: int
    type: str

# ---------------- API ----------------

@app.get("/")
def home():
    return {"message": "Server running"}

@app.post("/add-vehicle")
def add_vehicle(vehicle: Vehicle):
    if len(vehicle.bbox) != 4:
        return {"status": "error", "message": "bbox must have 4 values"}

    x1, y1, x2, y2 = vehicle.bbox

    cursor.execute("""
    INSERT INTO vehicles (vehicle_id, type, frame, x1, y1, x2, y2)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (vehicle.vehicle_id, vehicle.type, vehicle.frame, x1, y1, x2, y2))

    conn.commit()

    return {"status": "stored"}

@app.get("/summary")
def summary():
    cursor.execute("SELECT COUNT(DISTINCT vehicle_id) FROM vehicles")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT type, COUNT(*) FROM vehicles GROUP BY type")
    data = cursor.fetchall()

    result = {t: c for t, c in data}

    return {
        "total_vehicles": total,
        "by_type": result
    }

@app.get("/vehicles")
def get_vehicles():
    cursor.execute("SELECT * FROM vehicles")
    rows = cursor.fetchall()

    return {"data": rows}
@app.post("/alert")
def add_alert(alert: Alert):
    cursor.execute("""
    INSERT INTO alerts (vehicle_id, alert_type)
    VALUES (?, ?)
    """, (alert.vehicle_id, alert.type))

    conn.commit()

    return {"status": "alert stored"}

@app.get("/alerts")
def get_alerts():
    cursor.execute("SELECT * FROM alerts")
    rows = cursor.fetchall()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "vehicle_id": r[1],
            "type": r[2],
            "time": r[3]
        })

    return {"alerts": result}