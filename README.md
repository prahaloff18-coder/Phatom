# 🚗 AI Vehicle Tracking & Idle Detection System

This project is a real-time AI system that detects, tracks, and analyzes vehicle movement from video input. 
It identifies vehicles, assigns unique tracking IDs, and detects idle vehicles based on movement patterns. 
Alerts are generated and stored using a backend API.

---

## 🔍 Features

- 🚘 Real-time vehicle detection using YOLOv8  
- 🔄 Multi-object tracking with unique IDs  
- ⏱️ Idle vehicle detection (based on movement over time)  
- 🚨 Automatic alert generation for stationary vehicles  
- 🗄️ Backend API with database storage  
- 📊 Live visualization with bounding boxes and labels  

---

## ⚙️ Tech Stack

- Python  
- OpenCV  
- Ultralytics YOLOv8  
- FastAPI  
- SQLite  
- Requests  

---

## 🧠 How It Works

1. Video is processed frame-by-frame  
2. YOLO detects vehicles and assigns tracking IDs  
3. Each vehicle’s movement is tracked over time  
4. If a vehicle remains stationary for a threshold time → marked as **IDLE**  
5. Alert is generated and sent to backend  
6. Backend stores vehicle data and alerts in database  

---

## 🚀 API Endpoints

| Method | Endpoint        | Description |
|--------|---------------|------------|
| POST   | /add-vehicle  | Store detected vehicle |
| POST   | /alert        | Store idle alert |
| GET    | /vehicles     | Get all vehicles |
| GET    | /alerts       | Get all alerts |
| GET    | /summary      | Get vehicle stats |

---

## ▶️ How to Run

### 1️⃣ Clone Repository
nstall Dependencies
pip install -r requirements.txt
3️⃣ Start Backend Server
python -m uvicorn app:app
4️⃣ Run Detection System
python final_demo.py
📊 Output
Vehicles shown with bounding boxes and IDs
Idle vehicles highlighted in real-time
Alerts stored in backend and retrievable via API


🎯 Use Cases
Smart traffic monitoring
Parking violation detection
Urban surveillance systems
Road safety analytics


📌 Future Improvements
Speed estimation
Traffic heatmaps
Web dashboard visualization
Multi-camera support
