from ultralytics import YOLO
import joblib
import pandas as pd


# ==========================================
# LOAD MODELS
# ==========================================

gas_model = joblib.load("models/gas_risk_model_v1.joblib")

helmet_model = YOLO("models/vision/helmet/best.pt")
worker_model = YOLO("yolo11n.pt")
fire_smoke_model = YOLO("models/vision/fire_smoke/best.pt")


# ==========================================
# INPUTS
# ==========================================

IMAGE = "fire_test.jpg"

sensor_data = {
    "CH4": 0.85,
    "CO": 45,
    "CO2": 0.32,
    "O2": 19.1,
    "temperature": 34,
    "humidity": 82
}


# ==========================================
# GAS AI
# ==========================================

gas_df = pd.DataFrame([sensor_data])

gas_risk = gas_model.predict(gas_df)[0]

print("Gas Risk :", gas_risk)


# ==========================================
# VISION AI
# ==========================================

helmet_result = helmet_model(
    IMAGE,
    device=0,
    conf=0.25,
    verbose=False
)[0]

worker_result = worker_model(
    IMAGE,
    device=0,
    classes=[0],
    conf=0.35,
    verbose=False
)[0]

fire_smoke_result = fire_smoke_model(
    IMAGE,
    device=0,
    conf=0.55,
    verbose=False
)[0]


helmet_detected = False
no_helmet_detected = False
fire_detected = False
smoke_detected = False

for box in helmet_result.boxes:
    name = helmet_model.names[int(box.cls[0])]

    if name == "Hardhat":
        helmet_detected = True

    elif name == "NO-Hardhat":
        no_helmet_detected = True


worker_detected = len(worker_result.boxes) > 0


for box in fire_smoke_result.boxes:
    name = fire_smoke_model.names[int(box.cls[0])]

    if name == "fire":
        fire_detected = True

    elif name == "smoke":
        smoke_detected = True


# ==========================================
# VISION RISK
# ==========================================

if fire_detected:
    vision_risk = "CRITICAL"

elif smoke_detected:
    vision_risk = "WARNING"

elif no_helmet_detected:
    vision_risk = "WARNING"

else:
    vision_risk = "SAFE"


# ==========================================
# FINAL AI DECISION
# ==========================================

risk_order = {
    "SAFE": 0,
    "WARNING": 1,
    "DANGER": 2,
    "CRITICAL": 3
}

if risk_order[gas_risk] >= risk_order[vision_risk]:
    overall_risk = gas_risk
else:
    overall_risk = vision_risk


# ==========================================
# FINAL OUTPUT
# ==========================================

print()
print("=" * 45)
print("       MINE SAFETY AI DECISION")
print("=" * 45)

print(f"Gas Risk       : {gas_risk}")
print(f"Worker         : {'DETECTED' if worker_detected else 'NOT DETECTED'}")
print(f"Helmet         : {'HARDHAT' if helmet_detected else 'NO-HARDHAT' if no_helmet_detected else 'NOT DETECTED'}")
print(f"Fire           : {'DETECTED' if fire_detected else 'NOT DETECTED'}")
print(f"Smoke          : {'DETECTED' if smoke_detected else 'NOT DETECTED'}")
print(f"Vision Risk    : {vision_risk}")

print("-" * 45)
print(f"OVERALL RISK   : {overall_risk}")
print("=" * 45)