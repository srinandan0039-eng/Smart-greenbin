from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Simulated database/state
waste_data = {
    "bin_id": "Green-Bin-01",
    "capacity_kg": 50,
    "current_level_kg": 42,
    "status": "Pending Collection",
    "location": "Sector 4"
}

@app.get("/")
def home():
    return {"message": "Green Bin Smart Tracker is Online"}

@app.post("/reset")
def reset_env():
    # This is the endpoint your screenshot showed was failing!
    waste_data["current_level_kg"] = 0
    return {"status": "success", "message": "Bin emptied/Environment reset"}

@app.get("/analyze")
def analyze_data():
    capacity = waste_data["capacity_kg"]
    current = waste_data["current_level_kg"]
    
    # Logic to calculate pending work
    pending_kg = capacity - current
    fill_percentage = (current / capacity) * 100
    
    analysis = {
        "bin_id": waste_data["bin_id"],
        "fill_percentage": f"{fill_percentage}%",
        "pending_capacity_kg": pending_kg,
        "is_overloaded": current > capacity,
        "priority_level": "High" if fill_percentage > 80 else "Normal",
        "missing_tasks": []
    }
    
    # Identify which work is not done
    if fill_percentage > 90:
        analysis["missing_tasks"].append("Scheduled pickup missed")
    if current == 0:
        analysis["missing_tasks"].append("Sensor calibration needed")
        
    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
